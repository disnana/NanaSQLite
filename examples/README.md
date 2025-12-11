# NanaSQLite Examples

This directory contains practical examples demonstrating how to use NanaSQLite with popular Python frameworks.

## Available Examples

### 1. FastAPI Integration (`fastapi_integration.py`)

A complete user management API using AsyncNanaSQLite with FastAPI.

**Features:**
- Full CRUD operations (Create, Read, Update, Delete)
- Async/await support
- Pydantic models for validation
- Proper error handling
- Pagination support
- Dependency injection pattern

**Requirements:**
```bash
pip install fastapi uvicorn pydantic[email]
```

**Running:**
```bash
python fastapi_integration.py
# Visit http://localhost:8000/docs for interactive API documentation
```

**Example requests:**
```bash
# Create a user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "age": 30}'

# Get all users
curl http://localhost:8000/users

# Get specific user
curl http://localhost:8000/users/{user_id}

# Update user
curl -X PUT http://localhost:8000/users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{"age": 31}'

# Delete user
curl -X DELETE http://localhost:8000/users/{user_id}

# Get stats
curl http://localhost:8000/stats
```

---

### 2. Flask Integration (`flask_integration.py`)

A blog API using synchronous NanaSQLite with Flask.

**Features:**
- Blog post management
- Search functionality (by keyword and tag)
- Statistics endpoint
- RESTful API design
- Error handling

**Requirements:**
```bash
pip install flask
```

**Running:**
```bash
python flask_integration.py
# API available at http://localhost:5000
```

**Example requests:**
```bash
# Create a post
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Post", "content": "Hello World!", "author": "Alice", "tags": ["intro", "blog"]}'

# Get all posts
curl http://localhost:5000/posts

# Get specific post
curl http://localhost:5000/posts/{post_id}

# Update post
curl -X PUT http://localhost:5000/posts/{post_id} \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Search posts
curl "http://localhost:5000/posts/search?q=hello"
curl "http://localhost:5000/posts/search?tag=blog"

# Delete post
curl -X DELETE http://localhost:5000/posts/{post_id}

# Get stats
curl http://localhost:5000/stats
```

---

### 3. Async Demo (`async_demo.py`)

Demonstrates async features of NanaSQLite including concurrent operations, batch processing, and SQL operations.

**Running:**
```bash
python async_demo.py
```

---

## Testing the Examples

To validate that the example patterns work correctly without installing the frameworks:

```bash
python test_examples.py
```

This test script validates all the NanaSQLite patterns used in the examples, ensuring they work correctly with the library.

## Key Patterns Demonstrated

### Async Pattern (FastAPI)
```python
from nanasqlite import AsyncNanaSQLite
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    app.state.db = AsyncNanaSQLite("app.db", max_workers=10)
    yield
    await app.state.db.close()

async def get_user(user_id: str, db = Depends(get_db)):
    return await db.aget(f"user_{user_id}")
```

### Sync Pattern (Flask)
```python
from nanasqlite import NanaSQLite

def get_db():
    if not hasattr(app, 'database'):
        app.database = NanaSQLite("app.db")
    return app.database

@app.teardown_appcontext
def close_db(error):
    # Note: NanaSQLite doesn't require explicit closing in sync contexts
    # The database connection is automatically managed
    pass
```

## Best Practices

1. **Use context managers** for automatic resource cleanup
2. **Reuse database connections** across requests (singleton pattern)
3. **Use async version** (`AsyncNanaSQLite`) with async frameworks
4. **Use sync version** (`NanaSQLite`) with sync frameworks
5. **Close databases** on application shutdown
6. **Validate input** before storing in database
7. **Handle errors** appropriately (404, 400, 500)

## Further Reading

- [Tutorial](../docs/en/tutorial.md) - Step-by-step learning guide
- [Best Practices](../docs/en/best_practices.md) - Production tips
- [Async Guide](../docs/en/async_guide.md) - Async/await documentation
- [API Reference](../docs/en/reference.md) - Complete API documentation
