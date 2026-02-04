import asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from typing import Union, Type
from models_intraservice.models import IntraServiceUser as IntraServiceUserModel
from models_intraservice.models import IntraServiceCompany as IntraServiceCompanyModel
from schemas_intraservice.schemas import (
    IntraServiceUserResponse,
    IntraServiceCompanyResponse,
)
from schemas_intraservice.schemas import IntraServiceUser, IntraServiceCompany

from database.database import async_session_maker
from config import INTRASERVICE_URL
from operations_intrasevice.config import auth_user, IntraServiceData


class PostgresDataBase:
    def __init__(
        self,
        data: list[IntraServiceUser] | list[IntraServiceCompany],
        data_type: Union[
            Type[IntraServiceUserModel],
            Type[IntraServiceCompanyModel],
        ],
        fields_to_update: list[str],
    ):
        self.data = data
        self.data_type = data_type
        self.fields_to_update = fields_to_update

    async def add_to_db(self, async_session_maker):
        try:
            async with async_session_maker() as session:
                values = [item.model_dump() for item in self.data]
                stmt = insert(self.data_type).values(values)
                set_dict = {
                    field: getattr(stmt.excluded, field)
                    for field in self.fields_to_update
                }
                stmt = stmt.on_conflict_do_update(
                    index_elements=["id"],
                    set_=set_dict,
                )
                await session.execute(stmt)
                await session.commit()
        except SQLAlchemyError as err:
            print("Ошибка SQLAlchemy:", str(err))


async def get_data():
    host = INTRASERVICE_URL
    user_data = IntraServiceData(
        user=auth_user,
        host=host,
        url="/api/user",
        pagesize=1000,
        data_type=IntraServiceUserResponse,
    )

    users = await user_data.get_data()

    company_data = IntraServiceData(
        user=auth_user,
        host=host,
        url="/api/company",
        pagesize=1000,
        data_type=IntraServiceCompanyResponse,
    )

    companies = await company_data.get_data()

    # запись в бд
    company_update_fields = [
        "name",
        "fullname",
        "typeid",
        "isarchive",
    ]

    companies_db = PostgresDataBase(
        data=companies,
        fields_to_update=company_update_fields,
        data_type=IntraServiceCompanyModel,
    )

    await companies_db.add_to_db(async_session_maker)

    user_update_fields = [
        "name",
        "companyid",
        "email",
        "login",
        "mobilephone",
        "phone",
        "position",
        "isarchive",
    ]
    users_db = PostgresDataBase(
        data=users,
        fields_to_update=user_update_fields,
        data_type=IntraServiceUserModel,
    )

    await users_db.add_to_db(async_session_maker)


if __name__ == "__main__":
    asyncio.run(get_data())
