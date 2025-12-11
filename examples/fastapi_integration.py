#!/usr/bin/env python3
"""
FastAPI Integration Example with NanaSQLite

This example demonstrates how to use AsyncNanaSQLite with FastAPI
for a simple user management API.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from nanasqlite import AsyncNanaSQLite
from contextlib import asynccontextmanager
from typing import List, Optional
import uuid


# Pydantic models for request/response
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    age: int


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


# Application lifespan for database management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup, close on shutdown"""
    # Startup: Create database with optimized settings
    app.state.db = AsyncNanaSQLite(
        "users.db",
        max_workers=10,  # Handle 10 concurrent requests
        bulk_load=False  # Lazy loading for scalability
    )
    print("Database initialized")
    yield
    # Shutdown: Close database
    await app.state.db.close()
    print("Database closed")


# Create FastAPI app
app = FastAPI(
    title="User Management API",
    description="Simple user CRUD API using AsyncNanaSQLite",
    version="1.0.0",
    lifespan=lifespan
)


# Dependency injection for database
async def get_db() -> AsyncNanaSQLite:
    """Get database instance"""
    return app.state.db


# Routes
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: AsyncNanaSQLite = Depends(get_db)
):
    """Create a new user"""
    # Generate unique ID
    user_id = str(uuid.uuid4())
    
    # Check if email already exists
    all_users = await db.akeys()
    for key in all_users:
        if key.startswith("user_"):
            existing_user = await db.aget(key)
            if existing_user and existing_user.get("email") == user.email:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
    
    # Save user
    user_data = {
        "name": user.name,
        "email": user.email,
        "age": user.age
    }
    await db.aset(f"user_{user_id}", user_data)
    
    return UserResponse(id=user_id, **user_data)


@app.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncNanaSQLite = Depends(get_db)
):
    """List all users with pagination"""
    users = []
    all_keys = await db.akeys()
    user_keys = [k for k in all_keys if k.startswith("user_")]
    
    # Apply pagination
    for key in user_keys[skip:skip + limit]:
        user_id = key[5:]  # Remove "user_" prefix
        user_data = await db.aget(key)
        if user_data:
            users.append(UserResponse(id=user_id, **user_data))
    
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncNanaSQLite = Depends(get_db)
):
    """Get a specific user by ID"""
    user_data = await db.aget(f"user_{user_id}")
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(id=user_id, **user_data)


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: AsyncNanaSQLite = Depends(get_db)
):
    """Update a user"""
    # Check if user exists
    user_data = await db.aget(f"user_{user_id}")
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update.name is not None:
        user_data["name"] = user_update.name
    if user_update.email is not None:
        user_data["email"] = user_update.email
    if user_update.age is not None:
        user_data["age"] = user_update.age
    
    # Save updated user
    await db.aset(f"user_{user_id}", user_data)
    
    return UserResponse(id=user_id, **user_data)


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: AsyncNanaSQLite = Depends(get_db)
):
    """Delete a user"""
    # Check if user exists
    user_data = await db.aget(f"user_{user_id}")
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user
    await db.adelete(f"user_{user_id}")
    return None


@app.get("/stats")
async def get_stats(db: AsyncNanaSQLite = Depends(get_db)):
    """Get database statistics"""
    total_users = await db.alen()
    return {
        "total_users": total_users,
        "database": "users.db"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("Starting FastAPI server...")
    print("API documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
