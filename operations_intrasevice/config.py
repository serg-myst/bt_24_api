import base64
from typing import Union, Type, Optional
from fastapi import HTTPException, status
import aiohttp
from pydantic import ValidationError
from config import INTRASERVICE_USER, INTRASERVICE_USER_PASSWORD
from schemas_intraservice.schemas import (
    IntraServiceUserResponse,
    IntraServiceCompanyResponse,
    IntraServiceTaskResponse,
)


class UserAuth:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    def get_auth(self):
        token = base64.b64encode(
            f"{self.login}:{self.password}".encode("utf-8")
        ).decode("utf-8")
        return {"Authorization": f"Basic {token}"}


class IntraServiceData:
    def __init__(
        self,
        user: UserAuth,
        host: str,
        url: str,
        pagesize: int,
        data_type: Union[
            Type[IntraServiceUserResponse],
            Type[IntraServiceCompanyResponse],
            Type[IntraServiceTaskResponse],
        ],
        query_params: Optional[str] = (None,),
    ):
        self.user = user
        self.host = host
        self.url = url
        self.pagesize = pagesize
        self.data_type = data_type
        self.query_params = query_params

    async def get_data(self) -> list:
        data_list = []
        page = 1
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(
            timeout=timeout,
        ) as session:
            while True:
                try:
                    async with session.request(
                        method="get",
                        url=f"{self.host}{self.url}?fields={self.data_type.get_fields()}"
                        f"&page={page}&pagesize={self.pagesize}{self.query_params}",
                        headers=self.user.get_auth(),
                    ) as response:

                        if response.status == 200:
                            data = await response.json()
                            try:
                                items = self.data_type(**data)
                            except ValidationError as err:
                                """
                                raise HTTPException(
                                    status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Нет данных по заданным параметрам. Не прошло по схеме {err.json()}",
                                )
                                """
                                return data_list
                            else:
                                data_list.extend(items.get_items())

                            if page == items.paginator.PageCount:
                                break
                            page += 1

                        else:
                            raise HTTPException(
                                status_code=status.HTTP_417_EXPECTATION_FAILED,
                                detail=f"{response.status} {await response.text()}",
                            )
                except aiohttp.ClientError as err:
                    raise HTTPException(
                        status_code=status.HTTP_408_REQUEST_TIMEOUT,
                        detail=err,
                    )

        return data_list


auth_user = UserAuth(
    INTRASERVICE_USER,
    INTRASERVICE_USER_PASSWORD,
)
