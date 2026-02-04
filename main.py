from fastapi import FastAPI
from operations.router import router_department as router_departments
from operations.router import router_user as router_users
from operations.router import router_task as router_task
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from operations_intrasevice.views import router as intra_service_router

app = FastAPI(title="BT-24 API")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def welcome():
    return {
        "status": 200,
        "details": "welcome to our api. Read the instructions and go ahead",
        "data": [],
    }


app.include_router(router_departments)
app.include_router(router_users)
app.include_router(router_task)
app.include_router(
    intra_service_router,
    prefix="/intraservice",
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7000)
