from fastapi import FastAPI
from operations.router import router_department as router_departments
from operations.router import router_user as router_users
from operations.router import router_task as router_task
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='BT-24 API')

origins = [
    'http://localhost',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
