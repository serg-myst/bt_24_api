import asyncio
import aiohttp
from config import URL
from get_params import Params
from schemas.schemas import User
from pydantic import ValidationError


def get_content(request: dict) -> list:
    result = []
    match request:
        case {'result': result}:
            pass
    return result


async def get_users(session, department_id: int, users_list: list) -> list:
    method = 'user.get'
    params = {}
    fields = []
    http_params = Params(fields, params)
    http_params.add_filter('UF_DEPARTMENT', department_id)
    # http_params.add_filter('ACTIVE', 'true')
    params = http_params.get_params()
    async with session.request(method='get', url=f'{URL}/{method}', params=params) as response:
        if response.status == 200:
            content = await response.json()
            result = get_content(content)
            for data in result:
                try:
                    user = User(**data)
                except ValidationError as err:
                    print(f'Данные пользователя не прошли по схеме. {err.json()}')
                else:
                    users_list.append(user)
        else:
            print(f'Ошибка получения данных методом {method}. Статус {response.status_code}')


async def gather_users(departments: list, users_order_list):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for dep in departments:
            task = asyncio.create_task(get_users(session, dep.id, users_order_list))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def main(departments, user_list):
    await gather_users(departments, user_list)


if __name__ == '__main__':
    ...
