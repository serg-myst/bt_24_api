from pydantic import BaseModel, Field, computed_field, model_validator
from typing import List
from datetime import datetime
from config import INTRASERVICE_URL

TASK_STATUS_LABELS = {
    31: "Открыта",
    27: "В работе",
    35: "Требует уточнения",
    29: "Выполнена",
    36: "Согласование",
    28: "Закрыта",
    26: "Отложена",
    30: "Отменена",
    37: "Во внешней организации",
}


class IntraServiceUser(BaseModel):
    id: int = Field(alias="Id")
    companyid: int = Field(alias="CompanyId")
    email: str | None = Field(alias="Email", default=None)
    isarchive: bool = Field(alias="IsArchive")
    login: str = Field(alias="Login")
    mobilephone: str | None = Field(alias="MobilePhone", default=None)
    name: str = Field(alias="Name")
    phone: str | None = Field(alias="Phone", default=None)
    position: str | None = Field(alias="Position", default=None)


class IntraServiceCompany(BaseModel):
    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    fullname: str = Field(alias="FullName")
    isarchive: bool = Field(alias="IsArchive")
    typeid: int = Field(alias="TypeId")


class IntraServiceCompanyModelResponse(BaseModel):
    id: int
    name: str
    typeid: int = Field(exclude=True)

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def type(self) -> str:
        return {
            1: "наш отдел",
            2: "подрядчик",
        }.get(self.typeid, "неизвестно")


class Paginator(BaseModel):
    Count: int
    CountOnPage: int
    HasNextPage: bool | None = None
    Page: int
    PageCount: int
    PageSize: int


class IntraServiceUserResponse(BaseModel):
    paginator: Paginator = Field(alias="Paginator")
    users: List[IntraServiceUser] = Field(alias="Users")

    def get_items(self) -> list[IntraServiceUser]:
        return self.users

    @staticmethod
    def get_fields():
        return "id,Name,Login,Email,Phone,CompanyId,CompanyName,IsArchive,Position,MobilePhone"


class IntraServiceCompanyResponse(BaseModel):
    paginator: Paginator = Field(alias="Paginator")
    companies: List[IntraServiceCompany] = Field(alias="Companies")

    def get_items(self) -> list[IntraServiceCompany]:
        return self.companies

    @staticmethod
    def get_fields():
        return "id,Name,FullName,IsArchive,TypeId"


class IntraServiceTask(BaseModel):
    id: int = Field(alias="Id")
    creator_id: int = Field(alias="CreatorId")
    type_id: int = Field(alias="TypeId")
    creator: str = Field(alias="Creator")
    executors: str | None = Field(alias="Executors", default=None)
    executor_ids: str | None = Field(alias="ExecutorIds", default=None)
    observers: str = Field(alias="Observers")
    observer_ids: str = Field(alias="ObserverIds")
    name: str = Field(alias="Name")
    description: str = Field(alias="Description")
    status_id: int = Field(alias="StatusId")
    status: str | None = Field(alias="Status", default=None)
    created: datetime = Field(alias="Created")
    closed: datetime | None = Field(alias="Closed", default=None)
    deadline: datetime | None = Field(alias="Deadline", default=None)
    url: str | None = None

    def __repr__(self):
        return (
            f"id:{self.id}. Заявитель: {self.creator}. Испольнитель: {self.executors}"
        )

    def generate_url(self):
        return f"{INTRASERVICE_URL}Task/view/{self.id}"

    @model_validator(mode="after")
    def set_status_from_id(self):
        self.status = TASK_STATUS_LABELS.get(self.status_id, "Неизвестный статус")
        return self


class IntraServiceTaskResponse(BaseModel):
    paginator: Paginator = Field(alias="Paginator")
    tasks: List[IntraServiceTask] = Field(alias="Tasks")

    def get_items(self) -> list[IntraServiceTask]:
        return self.tasks

    @staticmethod
    def get_fields():
        return (
            "Id,Name,StatusId,Description,Created,Closed,Deadline,CreatorId,Creator,ExecutorIds,"
            "Executors,ObserverIds,Observers,TypeId,Type,ServiceId"
        )


class UserTasks(BaseModel):
    user_id: int | None = None
    user: str | None = None
    department_id: int | None = None
    tasks_in_work: List[IntraServiceTask] = Field(default=[])
    closed_tasks: List[IntraServiceTask] = Field(default=[])
    other_tasks: List[IntraServiceTask] = Field(default=[])


class IntraServiceUserTasksResponse(BaseModel):
    users_tasks: List[UserTasks] = Field(default=[])
    other_tasks: List[IntraServiceTask] = Field(default=[])
