from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from models_intraservice.models import IntraServiceUser, IntraServiceCompany
from schemas_intraservice.schemas import (
    IntraServiceTaskResponse,
    IntraServiceUserTasksResponse,
    UserTasks,
)
from operations_intrasevice.config import IntraServiceData, auth_user
from config import INTRASERVICE_URL


async def get_tasks(
    session: AsyncSession,
    closed_less_than: datetime,
    closed_more_than: datetime,
    department_in: int,
):
    stmt = select(
        IntraServiceUser.id,
        IntraServiceUser.name,
    ).where(
        and_(
            IntraServiceUser.companyid == department_in,
            IntraServiceUser.isarchive.is_(False),
        ),
    )
    result = await session.execute(stmt)
    items = result.mappings().all()

    users_id = ",".join(str(item["id"]) for item in items)

    """
    31 - Открыта
    27 - В работе
    35 - Требует уточнения
    29 - Выполнена
    36 - Согласование
    
    28 - Закрыта
    
    26 - Отложена
    30 - Отменена
    37 - Во внешней организации
    """

    # Открытые заявки
    host = INTRASERVICE_URL
    query_params = None
    if auth_user:
        query_params = f"&ExecutorIds={users_id}"
    query_params += "&StatusIds=31,27,35,29,36"
    user_tasks = IntraServiceData(
        user=auth_user,
        host=host,
        url="api/task",
        pagesize=1000,
        data_type=IntraServiceTaskResponse,
        query_params=query_params,
    )

    executors_task_list_in_work = await user_tasks.get_data()

    query_params = None
    if auth_user:
        query_params = f"&ObserverIds={users_id}"
    query_params += "&StatusIds=31,27,35,29,36"
    user_tasks = IntraServiceData(
        user=auth_user,
        host=host,
        url="api/task",
        pagesize=1000,
        data_type=IntraServiceTaskResponse,
        query_params=query_params,
    )

    observers_task_list = await user_tasks.get_data()

    # Оставим только заявки без исполнителей. С сиполнителем наверняка будут в первом запросе
    # или вообще на другом департаменте
    observers_task_list_in_work = list(
        filter(lambda task: not task.executors, observers_task_list)
    )

    # Закрытые задачи
    query_params = None
    if auth_user:
        query_params = f"&ExecutorIds={users_id}&ClosedMoreThan={closed_more_than}&ClosedLessThan={closed_less_than}"
    query_params += "&StatusIds=28"
    user_tasks = IntraServiceData(
        user=auth_user,
        host=host,
        url="api/task",
        pagesize=1000,
        data_type=IntraServiceTaskResponse,
        query_params=query_params,
    )

    closed_users_tasks = await user_tasks.get_data()

    # Остальные задачи
    query_params = None
    if auth_user:
        query_params = f"&ExecutorIds={users_id}&ClosedMoreThan={closed_more_than}&ClosedLessThan={closed_less_than}"
    query_params += "&StatusIds=26,30,36,37"
    user_tasks = IntraServiceData(
        user=auth_user,
        host=host,
        url="api/task",
        pagesize=1000,
        data_type=IntraServiceTaskResponse,
        query_params=query_params,
    )

    other_users_tasks = await user_tasks.get_data()

    response_list = IntraServiceUserTasksResponse(
        user_tasks=[],
        other_tasks=sorted(
            observers_task_list_in_work,
            key=lambda task: task.created,
        ),
    )

    # Разобьем задачи по пользователям
    for user in items:
        tasks_in_work = sorted(
            (
                task
                for task in executors_task_list_in_work
                if task.executor_ids == str(user.id)
            ),
            key=lambda task: task.created,
        )

        other_tasks = sorted(
            (task for task in other_users_tasks if task.executor_ids == str(user.id)),
            key=lambda task: task.created,
        )

        closed_tasks = sorted(
            (task for task in closed_users_tasks if task.executor_ids == str(user.id)),
            key=lambda task: task.created,
        )

        users_task_response = UserTasks(
            user=user.name,
            user_id=user.id,
            department_id=department_in,
            tasks_in_work=tasks_in_work,
            closed_tasks=closed_tasks,
            other_tasks=other_tasks,
        )

        response_list.users_tasks.append(users_task_response)

    return response_list


async def get_intra_service_departments_in_work(
    session: AsyncSession,
):
    stmt = (
        select(IntraServiceCompany)
        .where(IntraServiceCompany.is_active.is_(True))
        .order_by(
            IntraServiceCompany.id,
        )
    )
    result = await session.execute(stmt)
    return result.scalars().all()
