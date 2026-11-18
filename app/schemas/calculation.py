# app/schemas/calculation.py
"""
Calculation Pydantic Schemas

This module defines Pydantic schemas for validating calculation data at the
API boundary. Pydantic provides automatic validation, serialization, and
documentation generation for FastAPI.

Key Concepts:
- Schemas define the shape of data coming in/out of the API
- Validation happens automatically before data reaches your code
- Field validators provide custom validation logic
- Model validators can validate across multiple fields
- ConfigDict controls schema behavior and documentation

Design Pattern: Data Transfer Objects (DTOs)
These schemas act as DTOs, defining contracts between API and clients.
"""

from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    field_validator
)
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class CalculationType(str, Enum):
    """
    Enumeration of valid calculation types.
    
    Using an Enum provides:
    1. Type safety: Only valid values can be used
    2. Auto-completion: IDEs can suggest valid values
    3. Documentation: Automatically appears in OpenAPI spec
    4. Validation: Pydantic automatically rejects invalid values
    
    Inheriting from str makes this a string enum, so values serialize
    naturally as strings in JSON.
    """
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"


class CalculationBase(BaseModel):
    """
    Base schema for calculation data.
    
    This schema defines the common fields that all calculation requests share.
    It's used as a base for more specific schemas (Create, Update, Response).
    
    Design Pattern: This follows the DRY (Don't Repeat Yourself) principle by
    defining common fields once and reusing them in other schemas.
    """
    type: CalculationType = Field(
        ...,
        description="Type of calculation to perform",
        examples=["addition"]
    )
    inputs: List[float] = Field(
        ...,
        description="List of numeric inputs for the calculation",
        examples=[[10.5, 3, 2]],
        min_length=2
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v):
        """
        Validate and normalize the calculation type.
        
        This validator ensures that the type is a string and converts it to
        lowercase for case-insensitive comparison. It runs BEFORE Pydantic's
        standard validation (mode="before").
        
        Args:
            v: The value to validate
            
        Returns:
            The normalized (lowercase) type value
            
        Raises:
            ValueError: If the type is not a valid calculation type
        """
        allowed = {e.value for e in CalculationType}
        # Ensure v is a string and check (in lowercase) if it's allowed.
        if not isinstance(v, str) or v.lower() not in allowed:
            raise ValueError(
                f"Type must be one of: {', '.join(sorted(allowed))}"
            )
        return v.lower()

    @field_validator("inputs", mode="before")
    @classmethod
    def check_inputs_is_list(cls, v):
        """
        Validate that inputs is a list.
        
        This validator provides a clearer error message than Pydantic's
        default validation when inputs is not a list.
        
        Args:
            v: The value to validate
            
        Returns:
            The validated list
            
        Raises:
            ValueError: If inputs is not a list
        """
        if not isinstance(v, list):
            raise ValueError("Input should be a valid list")
        return v

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationBase":
        """
        Validate inputs based on calculation type.
        
        This is a model validator that runs AFTER all fields are validated.
        It can access multiple fields (self.type and self.inputs) to perform
        cross-field validation.
        
        Business Rules:
        1. All calculations require at least 2 inputs
        2. Division cannot have zero in denominators (positions 1+)
        
        This demonstrates LBYL (Look Before You Leap) - we validate before
        attempting the operation.
        
        Returns:
            self: The validated model instance
            
        Raises:
            ValueError: If validation fails
        """
        if self.type == CalculationType.DIVISION:
            # Prevent division by zero (skip first value as numerator)
            if any(x == 0 for x in self.inputs[1:]):
                raise ValueError("Cannot divide by zero")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"type": "addition", "inputs": [10.5, 3, 2]},
                {"type": "division", "inputs": [100, 2]}
            ]
        }
    )


class CalculationCreate(CalculationBase):
    """Validate legacy multi-operand and rubric two-operand calculations."""

    a: Optional[float] = None
    b: Optional[float] = None
    user_id: Optional[UUID] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_two_operands(cls, data):
        if not isinstance(data, dict):
            return data

        data = data.copy()
        has_a = "a" in data
        has_b = "b" in data

        if has_a or has_b:
            if not (has_a and has_b):
                raise ValueError("Both a and b are required")

            if "inputs" in data:
                raise ValueError("Provide either a/b or inputs, not both")

            data["inputs"] = [data["a"], data["b"]]

        elif "user_id" not in data:
            raise ValueError("user_id is required for legacy inputs")

        return data

    @model_validator(mode="after")
    def validate_legacy_user(self):
        return self

class CalculationUpdate(BaseModel):
    """
    Schema for updating an existing Calculation.
    
    This schema allows clients to update the inputs of an existing
    calculation. All fields are optional since partial updates are allowed.
    
    Note: The calculation type cannot be changed after creation. If you need
    a different type, create a new calculation.
    """
    inputs: Optional[List[float]] = Field(
        None,
        description="Updated list of numeric inputs for the calculation",
        examples=[[42, 7]],
        min_length=2
    )

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationUpdate":
        """
        Validate the inputs if they are being updated.
        
        Returns:
            self: The validated model instance
            
        Raises:
            ValueError: If inputs has fewer than 2 numbers
        """
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"inputs": [42, 7]}}
    )


class CalculationResponse(CalculationBase):
    """
    Schema for reading a Calculation from the database.
    
    This schema includes all the fields that are returned when reading
    a calculation, including database-generated fields like id, created_at,
    and the computed result.
    
    The from_attributes=True config allows this schema to be populated from
    SQLAlchemy model instances using model.from_orm(db_calculation).
    """
    id: UUID = Field(
        ...,
        description="Unique UUID of the calculation",
        examples=["123e4567-e89b-12d3-a456-426614174999"]
    )
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    created_at: datetime = Field(
        ...,
        description="Time when the calculation was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Time when the calculation was last updated"
    )
    result: float = Field(
        ...,
        description="Result of the calculation",
        examples=[15.5]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "addition",
                "inputs": [10.5, 3, 2],
                "result": 15.5,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    )


class CalculationRead(BaseModel):
    """Rubric-compatible output schema for two-operand calculations."""

    id: UUID
    a: float
    b: float
    type: CalculationType
    result: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value):
        if isinstance(value, str):
            value = value.lower()
        return value

    @model_validator(mode="after")
    def validate_division(self):
        if self.type == CalculationType.DIVISION and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self