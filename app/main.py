from fastapi import FastAPI

from app.user.endpoints import router as UserRouter

app = FastAPI()
app.include_router(UserRouter)


@app.get('/')
def hello_world():
    return {'message': 'Hello'}
