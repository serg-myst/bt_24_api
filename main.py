from fastapi import FastAPI
from operations.router import router_department as router_departments
from operations.router import router_user as router_users
from operations.router import router_task as router_task

app = FastAPI(title='BT-24 API')


@app.get('/', include_in_schema=False)
async def welcome():
    return {
        'status': 200,
        'details': 'welcome to our api. Read the instructions and go ahead',
        'data': []
    }


app.include_router(router_departments)
app.include_router(router_users)
app.include_router(router_task)
