import uuid

from sqlmodel import Session

from app import crud
from app.models import Customer, CustomerCreate
from tests.utils.utils import random_lower_string


def create_random_customer(db: Session) -> Customer:
    name = f"customer-{random_lower_string()}"
    customer_in = CustomerCreate(name=name, description="Test customer")
    return crud.create_customer(session=db, customer_in=customer_in)


def get_or_create_default_customer(db: Session) -> Customer:
    customer = crud.get_customer_by_name(session=db, name="Default")
    if customer:
        return customer
    return crud.create_customer(
        session=db,
        customer_in=CustomerCreate(name="Default", description="Default customer"),
    )
