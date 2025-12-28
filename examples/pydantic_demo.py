#!/usr/bin/env python3
"""
Pydantic Integration Example with NanaSQLite

This example demonstrates how to use Pydantic models with NanaSQLite
for data validation and type safety.
"""

import uuid
from typing import Optional

from pydantic import BaseModel, ValidationError, field_validator

from nanasqlite import NanaSQLite


# Pydantic models
class User(BaseModel):
    id: str
    name: str
    email: str
    age: int
    active: bool = True

    @field_validator('age')
    @classmethod
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        return v

    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v


class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    active: Optional[bool] = True

    @field_validator('age')
    @classmethod
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        return v

    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v


def main():
    """Demonstrate Pydantic integration with NanaSQLite"""
    print("=== Pydantic Integration Demo ===")

    # Initialize database
    db = NanaSQLite("pydantic_demo.db", bulk_load=False)

    try:
        # Create some users with validation
        users_data = [
            {"name": "Alice", "email": "alice@example.com", "age": 25},
            {"name": "Bob", "email": "bob@example.com", "age": 30},
            {"name": "Charlie", "email": "charlie@example.com", "age": 35},
        ]

        print("Creating users with Pydantic validation...")
        for user_data in users_data:
            try:
                # Validate input data
                user_create = UserCreate(**user_data)
                # Create full user model
                user = User(id=str(uuid.uuid4()), **user_create.model_dump())
                # Save to database
                db[user.id] = user.model_dump()
                print(f"Created user: {user.name}")
            except ValidationError as e:
                print(f"Validation error: {e}")

        # Try to create invalid user
        print("\nTrying to create invalid user...")
        try:
            UserCreate(name="Invalid", email="invalid-email", age=-5)
        except ValidationError as e:
            print(f"Caught validation error: {e}")

        # Retrieve and validate users
        print("\nRetrieving users from database...")
        for key in db.keys():
            if key.startswith("user_") or len(key) == 36:  # UUID length
                user_data = db[key]
                try:
                    user = User(**user_data)
                    print(f"Retrieved user: {user.name}, Age: {user.age}, Active: {user.active}")
                except ValidationError as e:
                    print(f"Data validation error for key {key}: {e}")

        # Update a user
        print("\nUpdating a user...")
        user_id = list(db.keys())[0]  # Get first user
        user_data = db[user_id]
        user = User(**user_data)
        user.age += 1
        db[user_id] = user.model_dump()
        print(f"Updated {user.name}'s age to {user.age}")

        # Demonstrate model methods
        print("\nDemonstrating model serialization...")
        user_dict = user.model_dump()
        print(f"User as dict: {user_dict}")

        user_json = user.model_dump_json()
        print(f"User as JSON: {user_json}")

    finally:
        # Cleanup
        db.close()
        print("\nDemo completed. Database closed.")


if __name__ == "__main__":
    main()
