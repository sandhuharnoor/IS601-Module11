import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine

from app import database
from app.models.user import User
from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)


def test_database_dependency_closes_session():
    fake_session = MagicMock()

    with patch.object(database, "SessionLocal", return_value=fake_session):
        generator = database.get_db()

        assert next(generator) is fake_session

        with pytest.raises(StopIteration):
            next(generator)

        fake_session.close.assert_called_once()


def test_get_engine_creates_engine():
    engine = database.get_engine("sqlite:///:memory:")

    try:
        assert engine.dialect.name == "sqlite"
    finally:
        engine.dispose()


def test_get_sessionmaker_creates_session():
    engine = create_engine("sqlite:///:memory:")

    try:
        factory = database.get_sessionmaker(engine)

        with factory() as session:
            assert session.get_bind() is engine
    finally:
        engine.dispose()


def test_user_repr():
    user = User(username="testuser", email="test@example.com")

    assert repr(user) == (
        "<User(username=testuser, email=test@example.com)>"
    )


def test_abstract_calculation_result_not_implemented():
    calculation = Calculation(
        user_id=uuid.uuid4(),
        inputs=[10, 5],
        type="calculation",
    )

    with pytest.raises(NotImplementedError):
        calculation.get_result()


def test_calculation_repr():
    calculation = Addition(
        user_id=uuid.uuid4(),
        inputs=[10, 5],
    )

    assert "Calculation(type=" in repr(calculation)
    assert "inputs=[10, 5]" in repr(calculation)


@pytest.mark.parametrize(
    "calculation_class",
    [Addition, Subtraction, Multiplication, Division],
)
def test_calculation_rejects_non_list_inputs(calculation_class):
    calculation = calculation_class(
        user_id=uuid.uuid4(),
        inputs="invalid",
    )

    with pytest.raises(ValueError, match="Inputs must be a list"):
        calculation.get_result()


@pytest.mark.parametrize(
    "calculation_class",
    [Addition, Subtraction, Multiplication, Division],
)
def test_calculation_rejects_insufficient_inputs(calculation_class):
    calculation = calculation_class(
        user_id=uuid.uuid4(),
        inputs=[10],
    )

    with pytest.raises(ValueError, match="at least two numbers"):
        calculation.get_result()

def test_create_rejects_both_operand_formats():
    from pydantic import ValidationError
    from app.schemas.calculation import CalculationCreate

    with pytest.raises(
        ValidationError,
        match="Provide either a/b or inputs, not both",
    ):
        CalculationCreate(
            type="addition",
            a=10,
            b=5,
            inputs=[10, 5],
        )


def test_create_rejects_non_dictionary_input():
    from pydantic import ValidationError
    from app.schemas.calculation import CalculationCreate

    with pytest.raises(ValidationError):
        CalculationCreate.model_validate("invalid")
import uuid
import pytest
from pydantic import ValidationError

from app.schemas.calculation import (
    CalculationBase,
    CalculationCreate,
    CalculationUpdate,
)

@pytest.mark.parametrize(
    "payload",
    [
        {"type": "addition", "inputs": [10]},
        {"type": "addition", "inputs": []},
    ],
)
def test_base_rejects_short_inputs(payload):
    with pytest.raises(ValidationError):
        CalculationBase.model_validate(payload)

@pytest.mark.parametrize(
    "payload",
    [
        {"type": "addition", "a": 10},
        {"type": "addition", "b": 5},
        {"type": "addition", "a": None, "b": None},
        {"type": "addition", "inputs": [10, 5]},
    ],
)
def test_create_rejects_missing_required_values(payload):
    with pytest.raises(ValidationError):
        CalculationCreate.model_validate(payload)

def test_update_rejects_short_inputs():
    with pytest.raises(ValidationError):
        CalculationUpdate(inputs=[10])

def test_legacy_create_still_accepts_valid_user():
    calculation = CalculationCreate(
        type="addition",
        inputs=[10, 5],
        user_id=uuid.uuid4(),
    )

    assert calculation.inputs == [10, 5]
