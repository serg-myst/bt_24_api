from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Annotated, List
from database.database import get_async_session
from operations_intrasevice.crud import get_tasks, get_intra_service_departments_in_work
from schemas_intraservice.schemas import (
    IntraServiceUserTasksResponse,
    IntraServiceCompanyModelResponse,
)

router = APIRouter(tags=["INTRASERVICE"])


@router.get(
    "/api/tasks",
    status_code=status.HTTP_200_OK,
    summary="метод возвращает заявки",
    response_model=IntraServiceUserTasksResponse,
)
async def get_intra_service_tasks(
    department: int,
    closedlessthan: Annotated[
        datetime,
        Query(description="Дата закрытия заявок меньше или равна указанной"),
    ],
    closedmorethan: Annotated[
        datetime, Query(description="Дата закрытия заявок больше или равна указанной")
    ],
    session: AsyncSession = Depends(get_async_session),
) -> IntraServiceUserTasksResponse:
    return await get_tasks(
        department_in=department,
        closed_less_than=closedlessthan,
        closed_more_than=closedmorethan,
        session=session,
    )


@router.get(
    "/api/departments",
    status_code=status.HTTP_200_OK,
    response_model=list[IntraServiceCompanyModelResponse],
)
async def get_intra_service_departments(
    session: AsyncSession = Depends(get_async_session),
) -> List[IntraServiceCompanyModelResponse]:
    return await get_intra_service_departments_in_work(
        session=session,
    )
