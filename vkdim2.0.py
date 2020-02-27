import requests
import time
import json
from urllib.parse import urlencode
from pprint import pprint

APP_ID = int(input('Введите APP_ID: '))
OUTH_URL = 'https://oauth.vk.com/authorize'
OUTH_PARAMS = {
    'client_id': APP_ID,
    'display': 'page',
    'scope': 'friends',
    'response_type': 'token',
    'v': '5.52'
}
print('Перейдите по ссылке ниже, скопируйте access_token и вставьте: ')
print('?'.join((OUTH_URL, urlencode(OUTH_PARAMS))))
token = input()

def main():
    while True:
        uid = input(
            'Введите ID (Nickname) пользователя, чтобы вывести список групп в которых он состоит, но не состоит никто из его друзей. ')
        user1 = User(uid)
        with open('groups.json', 'w', encoding='utf-8') as f:
            json.dump(user1.description_group(), f, ensure_ascii=False, indent=2)
            print('Файл успешно записан')
        next_step = input('Нажмите: \n'
                          'y - для повторного запуска\n'
                          'q - для выхода из программы\n')
        if next_step == 'y':
            continue
        elif next_step == 'q':
            break


def group_names(group):
    url = 'https://api.vk.com/method/groups.getById'
    params = {
        'group_id': group,
        'v': '5.52',
        'access_token': token,
    }
    response = requests.get(url, params=params)
    return response.json()['response'][0]['name']


class User:
    def __init__(self, uid):
        self.uid = uid
        self.link = 'https://vk.com/id' + str(self.uid)
        if requests.get(self.link).status_code == 404:
            self.get_user_uid()
            self.link = 'https://vk.com/id' + str(self.uid)
        self.groups_list = []

    def list_groups(self):
        url = 'https://api.vk.com/method/groups.get'
        params = {
            'user_id': self.uid,
            'v': '5.52',
            'count': 1000,
            'access_token': token,
        }
        response = requests.get(url, params=params)
        groups = []
        if 'error' in response.json().keys():
            pass
        else:
            for group in response.json()['response']['items']:
                groups.append(group)
        return set(groups)

    def set_groups(self):
        url = 'https://api.vk.com/method/friends.get'
        params = {
            'user_id': self.uid,
            'v': '5.52',
            'access_token': token,
        }
        response = requests.get(url, params=params)
        groups_main = self.list_groups()
        friends_count = len(response.json()['response']['items'])
        print(f'Обрабатывается {friends_count} друзей')
        for friend in response.json()['response']['items']:
            friend_groups = User(friend).list_groups()
            groups_main.difference_update(friend_groups)
            friends_count -= 1
            print(f'Осталось обработать {friends_count} друзей')
        return groups_main, len(groups_main)

    def description_group(self):
        url = 'https://api.vk.com/method/groups.getMembers'
        dict_groups = {}
        groups_main, groups_count = self.set_groups()
        print(f'Найдено {groups_count} группы, в которых состоит пользователь, но не состоят его друзья')
        for group in groups_main:
            params = {
                'group_id': group,
                'v': '5.52',
                'count': 0,
                'access_token': token,
            }
            response = requests.get(url, params=params)
            time.sleep(0.5)
            print(response.json())
            if 'error' in response.json().keys():
                pass
            else:
                dict_groups['name'] = group_names(group)
                dict_groups['gid'] = group
                dict_groups['members_count'] = response.json()['response']['count']
                self.groups_list.append(dict_groups)
                dict_groups = {}
                time.sleep(0.5)
            groups_count -= 1
            print(f'Осталось обработать {groups_count} групп')
        return self.groups_list

    def get_user_uid(self):
        url = 'https://api.vk.com/method/utils.resolveScreenName'
        params = {
            'screen_name': self.uid,
            'v': '5.52',
            'access_token': token,
        }
        response = requests.get(url, params=params)
        if response.json()['response'] == []:
            pass
        else:
            self.uid = response.json()['response']['object_id']

main()
