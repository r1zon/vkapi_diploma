import requests
import time
from urllib.parse import urlencode

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
        id1, id2 = map(int, input('Введите через пробел ID пользователей, для которых необходимо найти общих друзей: ').split())
        user1 = User(id1)
        user2 = User(id2)
        print('Первый пользователь: ', user1.first_name, user1.last_name, user1)
        print('Второй пользователь: ', user2.first_name, user2.last_name, user2)
        print()
        user1 & user2
        print()
        next_step = input('Нажмите: \n'
                          'y - для повторного ввода пары пользователей\n'
                          'q - для выхода из программы\n')
        if next_step == 'y':
            continue
        elif next_step == 'q':
            break

class User:
    def __init__(self, uid):
        self.uid = uid
        self.link = 'https://vk.com/id' + str(self.uid)
        url = 'https://api.vk.com/method/users.get'
        params = {
            'v': '5.52',
            'access_token': token,
            'user_ids': self.uid
        }
        response = requests.get(url, params=params)
        self.first_name = response.json()['response'][0]['first_name']
        self.last_name = response.json()['response'][0]['last_name']

    def __and__(self, other):
        url = 'https://api.vk.com/method/friends.getMutual'
        params = {
            'source_uid': self.uid,
            'v': '5.52',
            'access_token': token,
            'target_uid': other.uid
        }
        response = requests.get(url, params=params)
        try:
            if response.json()['response'] == []:
                print('Нет общих друзей')
            else:
                print('Список общих друзей: ')
                for i in response.json()['response']:
                    the_user = User(i)
                    print(f'{the_user.first_name} {the_user.last_name} ({the_user})')
                    time.sleep(0.5)
        except KeyError:
            print('Ошибка доступа')

    def __str__(self):
        return self.link

main()

