from config import URL, TASK_FIELDS
from schemas.schemas import Task
from pydantic import ValidationError
from .get_params import Params
import aiohttp
import asyncio
from pprint import pprint


def get_content(request: dict) -> list:
    user_tasks = []
    match request:
        case {'result': {'tasks': user_tasks}}:
            pass
    return user_tasks


async def get_tasks_by_parameters(session, params: dict):
    method = 'tasks.task.list'
    tasks_list = []
    async with session.request(method='get', url=f'{URL}/{method}', params=params) as response:
        if response.status == 200:
            content = await response.json()
            tasks = get_content(content)
            tasks_list = get_task_list(tasks, tasks_list)
            return tasks_list
        else:
            print(f'Ошибка получения данных методом {method}. Статус {response.status_code}')


async def get_user_tasks_by_parameters(session, params: dict, user):
    method = 'tasks.task.list'
    tasks_list = []
    async with session.request(method='get', url=f'{URL}/{method}', params=params) as response:
        if response.status == 200:
            content = await response.json()
            tasks = get_content(content)
            tasks_list = get_task_list(tasks, tasks_list)
            user.tasks.append(tasks_list)
        else:
            print(f'Ошибка получения данных методом {method}. Статус {response.status_code}')


def init_params(user_id: int, date1: str, date2: str) -> list:
    param_list = []
    params = {}
    task_closed_params = Params(TASK_FIELDS, params)
    task_closed_params.add_select()
    task_closed_params.add_filter('RESPONSIBLE_ID', user_id)
    task_closed_params.add_filter('>REAL_STATUS', 4)
    task_closed_params.add_filter('<=REAL_STATUS', 5)
    task_closed_params.add_filter('>=CLOSED_DATE', f"{date1}")
    task_closed_params.add_filter('<=CLOSED_DATE', f"{date2}")
    task_closed_params.add_order('CREATED_DATE', 'asc')

    param_list.append(task_closed_params)

    task_in_work_params = Params(TASK_FIELDS, params)
    task_in_work_params.add_select()
    task_in_work_params.add_filter('RESPONSIBLE_ID', user_id)
    task_in_work_params.add_filter('<=REAL_STATUS', 4)
    task_in_work_params.add_order('CREATED_DATE', 'asc')

    param_list.append(task_in_work_params)

    task_deferred_params = Params(TASK_FIELDS, params)
    task_deferred_params.add_select()
    task_deferred_params.add_filter('RESPONSIBLE_ID', user_id)
    task_deferred_params.add_filter('=REAL_STATUS', 6)
    task_deferred_params.add_order('CREATED_DATE', 'asc')

    param_list.append(task_deferred_params)

    task_declined_params = Params(TASK_FIELDS, params)
    task_declined_params.add_select()
    task_declined_params.add_filter('RESPONSIBLE_ID', user_id)
    task_declined_params.add_filter('=REAL_STATUS', 7)
    task_declined_params.add_order('CREATED_DATE', 'asc')

    param_list.append(task_declined_params)

    return param_list


async def get_user_tasks(session, user_id, user, date1: str, date2: str):
    param_list = init_params(user_id, date1, date2)
    for par in param_list:
        params = par.get_params()
        await get_user_tasks_by_parameters(session, params, user)


async def gather_tasks(user_list: list, date1: str, date2: str):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for current_user in user_list:
            task = asyncio.create_task(
                get_user_tasks(session, current_user.id, current_user, date1, date2))
            tasks.append(task)
        await asyncio.gather(*tasks)


def get_task_list(content: list, result: list) -> list:
    for data in content:
        try:
            task = Task(**data)
        except ValidationError as err:
            print(f'Данные задачи не прошли по схеме. {err.json()}')
        else:
            result.append(task)

    return result


if __name__ == '__main__':
    ...
