from get_departments import get_departments
from get_users_async import main
from operator import attrgetter
from sqlalchemy.dialects.sqlite import insert
from database.database import async_session_maker
from sqlalchemy.exc import SQLAlchemyError
from models.models import Department, User, DepartmentHead
import asyncio


async def save_data(item, table, id, session):
    try:
        insert_stmt = insert(table).values(item)
        do_update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=id,
            set_=item)
        await session.execute(do_update_stmt)
    except SQLAlchemyError as err:
        # save_error(str(err))
        print(str(err))


async def get_data():
    department_list = []
    department_head_list = []
    get_departments(department_list, department_head_list, 0)
    user_list = []
    await main(department_list, user_list)

    async with async_session_maker() as session:
        # department_list = sorted(department_list, key=attrgetter('id'))
        for dep in department_list:
            await save_data(dep.model_dump(), Department, ['id'], session)

        await session.commit()

    async with async_session_maker() as session:
        users_order_list = sorted(user_list, key=attrgetter('last_name'))
        for user in users_order_list:
            await save_data(user.model_dump(), User, ['id'], session)

        await session.commit()

    async with async_session_maker() as session:
        for head in department_head_list:
            if head.user_id != 0:
                await save_data(head.model_dump(), DepartmentHead, ['id'], session)

        await session.commit()


if __name__ == '__main__':
    asyncio.run(get_data())
