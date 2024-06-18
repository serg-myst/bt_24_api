from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional, Union, Any, Dict
from typing_extensions import Annotated
from config import EMPTY_DATE


class Department(BaseModel):
    id: int = Field(alias='ID')
    name: str = Field(alias='NAME')
    parent: Annotated[int | None, Field(alias='PARENT')] = None
    sort: int = Field(alias='SORT')

    # uf_head: Annotated[int | None, Field(alias='UF_HEAD')] = None

    def __repr__(self):
        return f'({self.id} {self.name})'


class Task(BaseModel):
    id: int
    status: int
    status_btx: int = Field(alias='status')
    status_real: int = Field(alias='status')
    title: str
    # description: str
    creator: Dict
    createdDate: datetime
    closedDate: Optional[datetime] = EMPTY_DATE
    deadline: Optional[datetime] = EMPTY_DATE

    @field_validator('status')
    def set_status(cls, s: int) -> str:
        match s:
            case 1:
                return "В работе"
            case 2:
                return "В работе"
            case 3:
                return "В работе"
            case 4:
                return "В работе"
            case 5:
                return "Завершена"
            case 6:
                return "Отложена"
            case 7:
                return "Завершена"
            case _:
                return "Не определено"

    @field_validator('status_btx')
    def set_btx_status(cls, s: int) -> str:
        match s:
            case 1:
                return "STATE_NEW"
            case 2:
                return "STATE_PENDING"
            case 3:
                return "STATE_IN_PROGRESS"
            case 4:
                return "STATE_SUPPOSEDLY_COMPLETED"
            case 5:
                return "STATE_COMPLETED"
            case 6:
                return "STATE_DEFERRED"
            case 7:
                return "STATE_DECLINED"
            case _:
                return "Не определено"


class User(BaseModel):
    id: int = Field(alias='ID')
    name: str = Field(alias='NAME')
    last_name: str = Field(alias='LAST_NAME')
    second_name: Annotated[str | None, Field(alias='SECOND_NAME')] = ''
    work_position: Annotated[str | None, Field(alias='WORK_POSITION')] = ''
    birthday: Annotated[str | datetime, Field(alias='PERSONAL_BIRTHDAY')]
    date_register: datetime = Field(alias='DATE_REGISTER')
    phone: Annotated[str | None, Field(alias='PERSONAL_MOBILE')] = ''
    email: Annotated[str | None, Field(alias='EMAIL')] = ''
    photo: Annotated[str | None, Field(alias='PERSONAL_PHOTO')] = None
    is_active: bool = Field(alias='ACTIVE')

    # department_id: List = Field(alias='UF_DEPARTMENT')

    @field_validator('birthday')
    def set_date(cls, d) -> datetime:
        if d == '':
            return EMPTY_DATE
        else:
            return datetime.strptime(d[:-6], '%Y-%m-%dT%H:%M:%S')

    '''
    @field_validator('department_id')
    def set_department(cls, d: List) -> int:
        if len(d) > 0:
            print(d)
            return int(d[0])
    '''

    def __repr__(self):
        return f'({self.id} {self.last_name} {self.name})'


class UserTasks(BaseModel):
    id: str = Field(alias='id')
    name: str = Field(alias='name')
    last_name: str = Field(alias='last_name')
    second_name: Annotated[str | None, Field(alias='second_name')] = ''
    tasks: Task = []


class DepartmentHead(BaseModel):
    department_id: int = Field(alias='ID')
    user_id: Annotated[int, Field(alias='UF_HEAD')] = 0

    def __repr__(self):
        return f'({self.id} {self.department_id} {self.user_id})'


class ResponseAnswer(BaseModel):
    status: int
    details: str | None
    data: list[Department] | None


class CloseTaskParams(BaseModel):
    user_id: int
    date_start: datetime
    date_stop: datetime
