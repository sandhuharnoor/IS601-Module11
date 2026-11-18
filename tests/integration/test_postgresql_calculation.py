import os
import uuid

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models.user import User
from app.models.calculation import Calculation, Addition, Division

DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/module11_test",
)


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(DATABASE_URL)
    if engine.url.database != "module11_test":
        raise RuntimeError("Integration tests require module11_test database")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_calculation_postgresql_persistence(db_engine):
    with Session(db_engine) as session:
        user = User(
            username=f"test_{uuid.uuid4().hex[:12]}",
            email=f"test_{uuid.uuid4().hex[:12]}@example.com",
        )
        session.add(user)
        session.flush()

        calculation = Calculation.create(
            "addition", user.id, [10, 20, 5]
        )
        calculation.result = calculation.get_result()
        session.add(calculation)
        session.commit()

        calculation_id = calculation.id

    with Session(db_engine) as session:
        saved = session.get(Calculation, calculation_id)

        assert saved is not None
        assert isinstance(saved, Addition)
        assert saved.inputs == [10, 20, 5]
        assert saved.result == 35
        assert saved.get_result() == 35


def test_calculation_postgresql_division(db_engine):
    with Session(db_engine) as session:
        user = User(
            username=f"test_{uuid.uuid4().hex[:12]}",
            email=f"test_{uuid.uuid4().hex[:12]}@example.com",
        )
        session.add(user)
        session.flush()

        calculation = Calculation.create(
            "division", user.id, [100, 4, 5]
        )
        calculation.result = calculation.get_result()
        session.add(calculation)
        session.commit()

        calculation_id = calculation.id

    with Session(db_engine) as session:
        saved = session.get(Calculation, calculation_id)

        assert isinstance(saved, Division)
        assert saved.result == 5
        assert saved.get_result() == 5

import uuid

from sqlalchemy.orm import Session

from app.models.calculation import Calculation
from app.models.user import User


def test_rubric_calculation_fields_persist(db_engine):
    """Verify rubric-required operands persist in PostgreSQL."""

    with Session(db_engine) as session:
        user = User(
            username=f"rubric_{uuid.uuid4().hex[:12]}",
            email=f"rubric_{uuid.uuid4().hex[:12]}@example.com",
        )
        session.add(user)
        session.flush()

        calculation = Calculation.create(
            "addition", user.id, [10, 5]
        )
        calculation.result = calculation.get_result()

        session.add(calculation)
        session.commit()

        calculation_id = calculation.id

    with Session(db_engine) as session:
        saved = session.get(Calculation, calculation_id)

        assert saved is not None
        assert saved.a == 10
        assert saved.b == 5
        assert saved.type == "addition"
        assert saved.result == 15
        assert saved.get_result() == 15
