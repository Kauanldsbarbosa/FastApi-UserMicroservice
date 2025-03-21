from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.auth.endpoints import router as AuthRouter
from app.user.endpoints import router as UserRouter

app = FastAPI()
app.include_router(UserRouter)
app.include_router(AuthRouter)


@app.get('/')
def hello_world():
    return RedirectResponse(url='/docs')
