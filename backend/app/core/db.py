from pgvector.psycopg import register_vector
from sqlalchemy import event
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import Customer, User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


@event.listens_for(engine, "connect")
def _register_pgvector(dbapi_connection: object, _connection_record: object) -> None:
    try:
        register_vector(dbapi_connection)
    except Exception:  # noqa: BLE001
        # Extension may not exist yet; migrations create it on first deploy.
        pass


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

    demo_customers = ["Customer A", "Customer B"]
    for name in demo_customers:
        existing = session.exec(select(Customer).where(Customer.name == name)).first()
        if not existing:
            session.add(Customer(name=name, description=f"Demo customer: {name}"))
    session.commit()
