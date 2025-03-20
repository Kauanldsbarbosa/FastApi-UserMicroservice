from fastapi import FastAPI

from app.user.endpoints import router as UserRouter
from app.auth.endpoints import router as AuthRouter

app = FastAPI()
app.include_router(UserRouter)
app.include_router(AuthRouter)


@app.get('/')
def hello_world():
    return {'message': 'Hello'}
