from typing import Optional, List
from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="FastAPI", version="0.1.0")

class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"

class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType

class Timestamp(BaseModel):
    id: int
    timestamp: int

class HTTPValidationError(BaseModel):
    detail: List['ValidationError']

class ValidationError(BaseModel):
    loc: List[str]
    msg: str
    type: str

dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]

@app.get("/",summary="Root",response_description="Successful Response")
async def root():
    return {"message": "Сервис ветеринарной клиники"}

@app.post("/post", summary="Get Post",response_model=Timestamp,response_description="Successful Response")
async def get_post(time: Timestamp):
    post_db.append(time)
    return time

@app.get("/dog",summary="Get Dogs",response_model=List[Dog],response_description="Successful Response")
async def get_dogs(kind: Optional[DogType] = None):
    if kind:
        return [d for d in dogs_db.values() if d.kind == kind]
    return list(dogs_db.values())

@app.post("/dog", summary="Create Dog", response_model=Dog, response_description="Successful Response")
async def create_dog(dog: Dog):
    if dog.pk in dogs_db:
        raise HTTPException(status_code=400, detail="Собака с таким id уже существует")
    dogs_db[dog.pk] = dog
    return dog

@app.get("/dog/{pk}", summary="Get Dog By Pk", response_model=Dog, response_description="Successful Response")
async def get_dog_pk(pk: int):
    if pk not in dogs_db:
        raise HTTPException(status_code=404, detail="Собака с таким id не найдена")
    return dogs_db[pk]

@app.patch("/dog/{pk}", summary="Update Dog", response_model=Dog, response_description="Successful Response")
async def update_dog(pk: int, dog: Dog):
    if pk not in dogs_db:
        raise HTTPException(status_code=404, detail="Собака не найдена")
    if pk != dog.pk:
        raise HTTPException(status_code=400, detail="Имеется несоответствие")
    dogs_db[pk] = dog
    return dog