from fastapi import FastAPI, Response, HTTPException, status
from sqlalchemy.sql.functions import mode
from fastapi.params import Depends
from sqlalchemy.orm import Session
from . import schemas
from . import models
from .database import engine, SessionLocal
from typing import List
from passlib.context import CryptContext

app = FastAPI()

models.Base.metadata.create_all(engine)

pwd_context = CryptContext(schemes= ['bcrypt'], deprecated = "auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.delete('/product/{id}')
def delete(id, db : Session = Depends(get_db)):
    db.query(models.Product).filter(models.Product.id == id).delete(synchronize_session = False)
    db.commit()
    return {'Product deleted'}

@app.get('/products', response_model = List[schemas.DisplayProduct])
def products(db : Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

@app.get('/product/{id}', response_model = schemas.DisplayProduct)
def product(id,response:Response, db : Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = 'Product not found')
    return product

@app.put('/product/{id}')
def update(id, request: schemas.Product , db : Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id)
    if not product.first():
        pass
    product.update(request.dict())
    db.commit()
    return {'Product successfully updated'}

@app.post('/product', status_code = status.HTTP_201_CREATED)
def add(request:schemas.Product, db : Session = Depends(get_db)):
    new_product = models.Product(name = request.name, description = request.description, price = request.price, seller_id = 1)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return request

@app.post('/seller', response_model = schemas.DisplaySeller)
def create_seller(request:schemas.Seller, db : Session = Depends(get_db)):
    hashedpassword = pwd_context.hash(request.password)
    new_seller = models.Seller(username = request.username, email = request.email, password = hashedpassword)
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    return new_seller