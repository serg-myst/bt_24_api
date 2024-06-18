from fastapi import APIRouter
from fastapi import Depends
from database.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Department as DepModel
from models.models import DepartmentHead, User
from sqlalchemy import select
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import selectinload
from schemas.schemas import CloseTaskParams
from services.get_params import Params
import aiohttp
from schemas.schemas import UserTasks
from services.get_tasks_async import get_tasks_by_parameters, gather_tasks
from pydantic import ValidationError
from pprint import pprint

router_department = APIRouter(
    prefix='/departments',
    tags=['Departments']
)

router_user = APIRouter(
    prefix='/users',
    tags=['Users']
)

router_task = APIRouter(
    prefix='/tasks',
    tags=['Tasks']
)


@router_department.get('/')
async def get_departments(session: AsyncSession = Depends(get_async_session)):
    query = select(DepModel).options(
        selectinload(DepModel.dep_head).joinedload(DepartmentHead.user, innerjoin=True)).where(DepModel.is_active)
    result = await session.scalars(query)

    return {
        'status': 200,
        'details': '',
        'data': result.all()
    }


@router_department.get('/{department_id}')
async def get_departments(department_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(DepModel).where(DepModel.is_active and DepModel.id == department_id)
    result = await session.scalars(query)

    return {
        'status': 200,
        'details': '',
        'data': result.all()
    }


@router_department.post('/{department_id}')
async def update_department(department_id: int, is_active: bool, session: AsyncSession = Depends(get_async_session)):
    query = select(DepModel).where(DepModel.id == department_id)
    item = await session.scalar(query)
    if not item:
        raise HTTPException(status_code=500, detail={
            'status': 500,
            'details': f'NotFound id={department_id}',
            'data': []
        })
    try:
        item.is_active = is_active
        await session.commit()
        return {
            'status': 200,
            'details': 'success',
            'data': [item]
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            'status': 500,
            'details': f"couldn't make changes id={department_id}",
            'data': []
        })


@router_user.get('/{department_id}')
async def get_departments(department_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.department_id == department_id).options(
        selectinload(User.user_department)).where(User.is_active).order_by('last_name')
    result = await session.scalars(query)

    return {
        'status': 200,
        'details': '',
        'data': result.all()
    }


@router_task.get('/tasks-in-work/{user_id}')
async def get_tasks_in_work(user_id: int):
    fields = ["ID", "TITLE", "STATUS", "CREATED_DATE", "CREATED_BY", "CLOSED_DATE", "DEADLINE"]
    params = {}
    task_params = Params(fields, params)
    task_params.add_select()
    task_params.add_filter('RESPONSIBLE_ID', user_id)
    task_params.add_filter('<=REAL_STATUS', 4)
    task_params.add_order('CREATED_DATE', 'asc')

    async with aiohttp.ClientSession() as session:
        user_tasks = await get_tasks_by_parameters(session, task_params.get_params())
        return {
            'status': 200,
            'details': '',
            'data': [task.model_dump() for task in user_tasks]
        }


@router_task.post('/tasks-closed/')
async def get_tasks_closed(request_params: CloseTaskParams):
    fields = ["ID", "TITLE", "STATUS", "CREATED_DATE", "CREATED_BY", "CLOSED_DATE", "DEADLINE"]
    params = {}
    task_params = Params(fields, params)
    task_params.add_select()
    task_params.add_filter('RESPONSIBLE_ID', request_params.user_id)
    task_params.add_filter('>REAL_STATUS', 4)
    task_params.add_filter('<=REAL_STATUS', 5)
    task_params.add_filter('>=CLOSED_DATE', f"{request_params.date_start}")
    task_params.add_filter('<=CLOSED_DATE', f"{request_params.date_stop}")
    task_params.add_order('CREATED_DATE', 'asc')

    async with aiohttp.ClientSession() as session:
        user_tasks = await get_tasks_by_parameters(session, task_params.get_params())
        return {
            'status': 200,
            'details': '',
            'data': [task.model_dump() for task in user_tasks]
        }


@router_task.get('/tasks-deferred/{user_id}')
async def get_tasks_in_work(user_id: int):
    fields = ["ID", "TITLE", "STATUS", "CREATED_DATE", "CREATED_BY", "CLOSED_DATE", "DEADLINE"]
    params = {}
    task_params = Params(fields, params)
    task_params.add_select()
    task_params.add_filter('RESPONSIBLE_ID', user_id)
    task_params.add_filter('=REAL_STATUS', 6)
    task_params.add_order('CREATED_DATE', 'asc')

    async with aiohttp.ClientSession() as session:
        user_tasks = await get_tasks_by_parameters(session, task_params.get_params())
        return {
            'status': 200,
            'details': '',
            'data': [task.model_dump() for task in user_tasks]
        }


@router_task.post('/department-tasks/{dep_id}')
async def get_department_tasks(request_params: CloseTaskParams, dep_id: int,
                               session: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.department_id == dep_id).options(
        selectinload(User.user_department)).where(User.is_active).order_by('last_name')
    result = await session.scalars(query)
    users = result.all()
    user_list = []
    for user in users:
        try:
            user_tasks = UserTasks(**user.dump_to_json())
        except ValidationError as err:
            print(f'Данные задачи не прошли по схеме. {err.json()}')
        else:
            user_list.append(user_tasks)

    await gather_tasks(user_list, request_params.date_start, request_params.date_stop)

    return {
        'status': 200,
        'details': '',
        'data': [user.model_dump() for user in user_list]
    }
