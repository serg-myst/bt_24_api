from config import URL
from schemas.schemas import Task
from pydantic import ValidationError


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
