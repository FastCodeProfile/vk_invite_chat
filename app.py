import asyncio
import json
import random
import string
from contextlib import suppress

import aiohttp
from loguru import logger


class VkApi:
    def __init__(self, access_token: str) -> None:
        self.host = 'https://api.vk.com/method/'
        self.params = {'v': 5.131}
        self.headers = {'Authorization': f"Bearer {access_token}"}

    async def invite_chat(self, chat_id: str, user_id: str) -> tuple[bool, str | dict]:
        method = 'messages.addChatUser'
        self.params["chat_id"] = chat_id
        self.params["user_id"] = user_id
        self.params["visible_messages_count"] = 100
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.host + method, params=self.params) as response:
                json_response = await response.json()
                if 'error' in json_response:
                    return False, json_response["error"]["error_msg"]
                else:
                    return True, json_response

    async def messages_search(self, rand_string: str) -> tuple[bool, str | int]:
        method = 'messages.search'
        self.params["q"] = rand_string
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.host + method, params=self.params) as response:
                json_response = await response.json()
                if 'error' in json_response:
                    return False, json_response['error']['error_msg']
                else:
                    return True, json_response['response']['items'][0]['peer_id'] - 2000000000


def load_data(filename: str) -> dict:
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


async def main() -> None:
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for _ in range(25))
    print(f'Отправьте эту строку "{random_string}" в нужный чат, после нажмите Enter.')
    input()
    data = load_data('data.json')
    for key, user in data.items():
        next_key = str(int(key) + 1)
        if next_key in data:
            next_user = data[next_key]
            vk_api = VkApi(user["access_token"])
            result = await vk_api.messages_search(random_string)
            next_result = await vk_api.invite_chat(result[1], next_user["user_id"])
            if result[0] and next_result[0]:
                logger.success(f'{user["url_profile"]} -> ДОБАВИЛ -> {next_user["url_profile"]}')
            else:
                logger.error(f'{user["url_profile"]} <- ЦЕПЬ РАЗОРВАНА -> {next_user["url_profile"]}')
                logger.warning('Используйте скрипт, что бы отсеять невалидные аккаунты. '
                               'Ссылка на скрипт: https://github.com/FastCodeProfile/vk_check_token.git')
                break


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
