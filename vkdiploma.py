import requests
import time
import datetime
import json
from urllib.parse import urlencode
from pprint import pprint
import copy

# APP_ID = int(input('Введите APP_ID: '))
APP_ID = 7334043

OUTH_URL = 'https://oauth.vk.com/authorize'
OUTH_PARAMS = {
    'client_id': APP_ID,
    'display': 'page',
    'scope': 'friends, groups',
    'response_type': 'token',
    'v': '5.52'
}
print('Перейдите по ссылке ниже, скопируйте access_token и вставьте: ')
print('?'.join((OUTH_URL, urlencode(OUTH_PARAMS))))
# token = input()
token = '86dd461ba73f80884b39e9ae6b6a4d555819a871fc77b1936ca805676de4a849c7c049c3bf410f20cef61'

def main():
    while True:
        uid = input(
            'Введите ID (Nickname) пользователя, чтобы вывести список групп в которых он состоит, но не состоит никто из его друзей. ')
        print()
        with timer() as t:
            user1 = User(uid)
            if user1.uid is None:
                continue
            with open('groups.json', 'w', encoding='utf-8') as f:
                file = user1.description_group(t)
                if file is None:
                    continue
                else:
                    json.dump(file, f, ensure_ascii=False, indent=2)
                    print('Файл успешно записан')
                    print()
                    print(f'Пользователь с id - {uid} обработан за {t.work_time()} секунд')
                    t.cancel_time()
            print()
            next_step = input('Нажмите: \n'
                              'y - для повторного запуска\n'
                              'q - для выхода из программы\n')

            if next_step == 'y':
                continue
            elif next_step == 'q':
                break


def user_get(uid):
    url = 'https://api.vk.com/method/users.get'
    params = {
        'v': 5.52,
        'access_token': token,
        'user_ids': uid
    }
    try:
        response = requests.get(url, params=params)
        if 'error' in response.json() and 'error_code' in response.json()['error'] and response.json()['error']['error_code'] == 113:
            raise InvalidUserID()
    except InvalidUserID:
        print(f'Неправильно введен ID {uid} пользователя')
        pass
    else:
        return response.json()['response'][0]['id']


class User:
    def __init__(self, uid):
        self.uid = user_get(uid)
        self.link = 'https://vk.com/id' + str(self.uid)
        self.groups_list = []

    def get_groups(self):
        url = 'https://api.vk.com/method/groups.get'
        params = {
            'v': 5.52,
            'access_token': token,
            'user_id': self.uid
        }
        try:
            response = requests.get(url, params=params)
            if 'error' in response.json() and 'error_code' in response.json()['error'] and response.json()['error']['error_code'] == 18:
                raise DeletedUser()
            if 'error' in response.json() and 'error_code' in response.json()['error'] and response.json()['error']['error_code'] == 15:
                raise PrivateUserProfile()
        except DeletedUser:
            print(f'Пользователь с ID {self.uid} удален или забанен')
            pass
        except PrivateUserProfile:
            print(f'Пользователь с ID {self.uid} запретил доступ к профилю')
            pass
        else:
            return response.json()['response']['items']

    def set_groups(self, t):
        url = 'https://api.vk.com/method/execute/'
        groups_main = self.get_groups()
        groups_temp = copy.deepcopy(groups_main)
        dict_friends = {'user_id': self.uid}
        groups_count = len(groups_temp)
        print()
        print(f'Поиск искомых групп среди {groups_count} групп пользователя')
        for group in groups_temp:
            dict_group = f"'group_id': {group}"
            code = str('var friends = API.groups.isMember({') + str(dict_group) + str(
                ", 'user_ids': API.friends.get(") + str(dict_friends) + str(').items}); return friends;')
            # code = 'var friends = API.groups.isMember({"group_id": 8564, "user_ids": API.friends.get({"user_id": 171691064}).items});' \
            #        'return friends;'
            params = {
                'v': 5.52,
                'access_token': token,
                'code': code
            }
            response = requests.get(url, params=params)
            repeat = True
            try:
                while repeat:
                    response = requests.get(url, params=params)
                    if 'error' in response.json() and 'error_code' in response.json()['error'] and response.json()['error']['error_code'] == 6:
                        time.sleep(0.34)
                    else:
                        repeat = False
                if 'error' in response.json() and 'error_code' in response.json()['error'] and response.json()['error']['error_code'] == 15:
                    raise GroupAccessDenied()
            except GroupAccessDenied:
                print(f'Отсутсвует доступ в группу с id {group}')
            else:
                for i in range(len(response.json()['response'])):
                    if response.json()['response'][i]['member'] == 1:
                        groups_main.remove(group)
                        break
            groups_count -= 1
            print(f'Осталось обработать {groups_count} групп')
        print()
        print(f'Поиск искомых групп выполнен за {t.work_time()} секунд\n')
        return groups_main, len(groups_main)

    def description_group(self, t):
        try:
            groups_main, groups_count = self.set_groups(t)
        except Exception:
            pass
        else:
            dict_groups = {}
            url = 'https://api.vk.com/method/execute/'
            print(f'Найдено {groups_count} группы, в которых состоит пользователь, но не состоят его друзья')
            for group in groups_main:
                dict_group = {'group_id': group}
                code = f'var groups_users_count = API.groups.getMembers({dict_group});' \
                       f'var groups_name = API.groups.getById({dict_group});' \
                       'return [groups_users_count.count, groups_name@.name];'
                params = {
                    'v': 5.52,
                    'access_token': token,
                    'code': code
                }
                repeat = True
                while repeat:
                    response = requests.get(url, params=params)
                    if 'error' in response.json() and 'error_code' in response.json()['error'] and response.json()['error']['error_code'] == 6:
                        time.sleep(0.34)
                    else:
                        repeat = False
                groups_users_count, groups_name = response.json()['response']
                dict_groups['name'] = groups_name[0]
                dict_groups['gid'] = group
                dict_groups['members_count'] = groups_users_count
                self.groups_list.append(dict_groups)
                dict_groups = {}
                groups_count -= 1
                print(f'Осталось обработать {groups_count} групп')
            print()
            return self.groups_list


class timer():
    def __init__(self):
        self.start = time.time()
        self.work = time.time()
        self.start_time = datetime.datetime.now()
        print(f'Время начала работы программы: {self.start_time}')

    def current_time(self):
        return round(time.time() - self.start, 2)

    def work_time(self):
        return round(time.time() - self.work, 2)

    def cancel_time(self):
        self.work = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.datetime.now()
        print(f'Программа завершилась в: {self.end_time}')
        print(f'Затрачено времени {self.current_time()} секунд')

class DeletedUser(Exception):
    pass

class GroupAccessDenied(Exception):
    pass

class PrivateUserProfile(Exception):
    pass

class InvalidUserID(Exception):
    pass

main()
