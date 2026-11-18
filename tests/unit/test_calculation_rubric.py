import uuid

import pytest
from pydantic import ValidationError
from sqlalchemy import inspect

from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationRead


def test_required_sqlalchemy_columns():
    columns = {column.key for column in inspect(Calculation).columns}
    assert {"id", "a", "b", "type", "result"}.issubset(columns)


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("addition", 10, 5, 15),
        ("subtraction", 10, 5, 5),
        ("multiplication", 10, 5, 50),
        ("division", 10, 5, 2),
    ],
)
def test_two_operand_calculations(operation, a, b, expected):
    data = CalculationCreate(a=a, b=b, type=operation)
    calculation = Calculation.create(
        data.type.value, uuid.uuid4(), data.inputs
    )

    assert calculation.a == a
    assert calculation.b == b
    assert calculation.get_result() == expected


@pytest.mark.parametrize(
    "data",
    [
        {"a": 10, "type": "addition"},
        {"b": 5, "type": "addition"},
        {"a": 10, "b": 5, "type": "modulus"},
        {"a": 10, "b": 0, "type": "division"},
        {"a": "invalid", "b": 5, "type": "addition"},
    ],
)
def test_invalid_calculation_create(data):
    with pytest.raises(ValidationError):
        CalculationCreate(**data)


def test_calculation_read_serialization():
    calculation = CalculationRead(
        id=uuid.uuid4(),
        a=10,
        b=5,
        type="addition",
        result=15,
    )

    output = calculation.model_dump(mode="json")

    assert output["a"] == 10
    assert output["b"] == 5
    assert output["result"] == 15
    assert "password" not in output
    assert "hashed_password" not in output


def test_calculation_read_rejects_zero_divisor():
    with pytest.raises(ValidationError):
        CalculationRead(
            id=uuid.uuid4(),
            a=10,
            b=0,
            type="division",
            result=None,
        )
