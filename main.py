import json
import random
import string
import asyncio
from contextlib import suppress

import aiohttp


class VK:
    """
    Класс для взаимодействия с ВК
    """

    def __init__(self, token: str) -> None:
        """
        Метод инициализации класса

        :param token: Токен аккаунта ВК
        """
        self.headers = {'Authorization': f'Bearer {token}'}

    async def invite_chat(self, chat_id: str, user_id: str) -> tuple[bool, str | dict]:
        """
        Метод для приглашения в чат ВК

        :return: tuple[bool, str | dict]
        """
        params = dict(
            chat_id=chat_id,
            user_id=user_id,
            visible_messages_count=100,
            v=5.131
        )
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f'https://api.vk.com/method/messages.addChatUser', params=params) as response:
                json_response = await response.json()
                if 'error' in json_response:
                    return False, json_response["error"]["error_msg"]
                else:
                    return True, json_response

    async def messages_search(self, rand_string: str) -> tuple[bool, str | int]:
        """
        Метод ищет чат по отправленной в него строке

        :param rand_string: Строка для поиска
        :return: tuple[bool, str | int]
        """
        params = dict(
            q=rand_string,
            v=5.131
        )
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f'https://api.vk.com/method/messages.search', params=params) as response:
                json_response = await response.json()
                if 'error' in json_response:
                    return False, json_response['error']['error_msg']
                else:
                    return True, json_response['response']['items'][0]['peer_id'] - 2000000000


def file_input() -> dict:
    """
    Функция читает и возвращает словарь с данными аккаунтов

    :return: dict
    """
    with open('./input.json', 'r') as file:
        return json.load(file)


async def main() -> None:
    """
    Главная функция запуска

    :return: None
    """
    letters = string.ascii_lowercase  # Все буквы
    random_string = ''.join(random.choice(letters) for i in range(25))  # Рандомный набор букв
    print(f'Отправьте эту строку "{random_string}" в нужный чат, после нажмите Enter.')
    input()  # Ждём пока отправят строку в чат, а после нажмут Enter
    input_data = file_input()  # Получаем словарь с данными аккаунтов
    for key in input_data.keys():  # Перебираем словарь по его ключам
        account = input_data[key]
        try:
            next_account = input_data[str(int(key) + 1)]
        except KeyError:
            break
        vk = VK(token=account["access_token"])  # Инициализируем класс
        status, response = await vk.messages_search(random_string)  # Пытаемся получить id-чата
        if status:  # Если id-чата получен
            next_status, next_response = await vk.invite_chat(response, next_account["user_id"])  # Добавляем в чат
            if next_status:  # Если добавление в чат прошло успешно
                print(f'{account["url_profile"]} добавил {next_account["url_profile"]}')
            else:  # Если добавление в чат прошло неуспешно
                print(f'Возникла ошибка - {next_account["url_profile"]}: {next_response}')
        else:  # Если id-чата не получен
            print(f'Возникла ошибка - {account["url_profile"]}: {response}')


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):  # Игнорирование ошибок при остановке
        asyncio.run(main())  # Запуск асинхронной функции из синхронного контекста
