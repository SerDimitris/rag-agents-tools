import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Customer,
    CustomerCreate,
    CustomerPublic,
    CustomersPublic,
    CustomerUpdate,
    Document,
    Message,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=CustomersPublic)
def read_customers(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
) -> Any:
    """
    Retrieve customers for the selection dropdown.
    """
    filters = []
    if not include_inactive:
        filters.append(Customer.is_active == True)  # noqa: E712

    count_statement = select(func.count()).select_from(Customer)
    if filters:
        count_statement = count_statement.where(*filters)
    count = session.exec(count_statement).one()

    statement = select(Customer).order_by(col(Customer.name).asc()).offset(skip).limit(limit)
    if filters:
        statement = statement.where(*filters)
    customers = session.exec(statement).all()

    return CustomersPublic(
        data=[CustomerPublic.model_validate(customer) for customer in customers],
        count=count,
    )


@router.post("/", response_model=CustomerPublic, dependencies=[Depends(get_current_active_superuser)])
def create_customer(
    *,
    session: SessionDep,
    customer_in: CustomerCreate,
) -> Any:
    """
    Create a new customer (superuser only).
    """
    existing = crud.get_customer_by_name(session=session, name=customer_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this name already exists")
    return crud.create_customer(session=session, customer_in=customer_in)


@router.get("/{id}", response_model=CustomerPublic)
def read_customer(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get customer by ID.
    """
    customer = session.get(Customer, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{id}", response_model=CustomerPublic, dependencies=[Depends(get_current_active_superuser)])
def update_customer(
    *,
    session: SessionDep,
    id: uuid.UUID,
    customer_in: CustomerUpdate,
) -> Any:
    """
    Update a customer (superuser only).
    """
    customer = session.get(Customer, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_dict = customer_in.model_dump(exclude_unset=True)
    if "name" in update_dict and update_dict["name"] != customer.name:
        existing = crud.get_customer_by_name(session=session, name=update_dict["name"])
        if existing:
            raise HTTPException(
                status_code=400, detail="Customer with this name already exists"
            )

    customer.sqlmodel_update(update_dict)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.delete("/{id}", dependencies=[Depends(get_current_active_superuser)])
def delete_customer(
    session: SessionDep,
    id: uuid.UUID,
) -> Message:
    """
    Delete a customer (superuser only). Blocked if documents exist.
    """
    customer = session.get(Customer, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    document_count = session.exec(
        select(func.count()).select_from(Document).where(Document.customer_id == id)
    ).one()
    if document_count:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete customer with existing documents",
        )

    session.delete(customer)
    session.commit()
    return Message(message="Customer deleted successfully")
