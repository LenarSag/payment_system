import asyncio

import uvicorn
from fastapi import FastAPI, status
from fastapi.exceptions import ValidationException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from db.database import init_models
from routers.login import loginrouter
from routers.users import usersrouter
from routers.transaction import transactionsrouter


API_PATH = "/api"


app = FastAPI()

app.include_router(loginrouter, prefix=f"{API_PATH}/auth")
app.include_router(usersrouter, prefix=f"{API_PATH}/users")
app.include_router(transactionsrouter, prefix=f"{API_PATH}/transaction")


@app.exception_handler(ValidationException)
async def custom_pydantic_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()}
    )


@app.exception_handler(ValidationError)
async def custom_pydantic_validation_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()}
    )


@app.get("/")
async def index():
    return "Payment system"


# Для запуска в контейнере Docker
async def startup_event():
    await init_models()

app.add_event_handler("startup", startup_event)

# для запуска без контейнера Docker
# if __name__ == "__main__":
#     asyncio.run(init_models())
#     uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
