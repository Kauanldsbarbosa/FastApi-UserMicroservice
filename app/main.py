from fastapi import FastAPI


app = FastAPI()

@app.get('/')
def hello_world():
    return {'message': 'Hello'}

# from config.config import config


# print(config.DATABASE_URL)