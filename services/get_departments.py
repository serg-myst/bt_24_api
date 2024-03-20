from config import URL
import requests
import json
from schemas.schemas import Department, DepartmentHead
from pydantic import ValidationError


def get_content(request: dict) -> list:
    result = []
    match request:
        case {'result': result}:
            pass
    return result


def get_next(request: dict) -> int:
    next_value = 0
    match request:
        case {'next': next_value}:
            pass
    return next_value


def get_departments(department_list: list, department_head_list: list, start: int):
    method = 'department.get'

    params = {
        "start": start,
    }

    response = requests.get(f'{URL}/{method}', params=params)
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
    else:
        content = json.loads(response.content)
        result = get_content(content)
        next_value = get_next(content)
        for data in result:
            try:
                department = Department(**data)
                department_head = DepartmentHead(**data)
            except ValidationError as err:
                print(f'Данные отдела не прошли по схеме. {err.json()}')
            else:
                department_list.append(department)
                department_head_list.append(department_head)
        if next_value != 0:
            get_departments(department_list, department_head_list, next_value)


if __name__ == '__main__':
    ...
