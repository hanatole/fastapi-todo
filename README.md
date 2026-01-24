# Todo

Fastapi based API of Todo application

## Installation and Running

Using `uv`, create a virtual environment and install the dependencies:

```shell

uv sync
uv run uvicorn api:app --host 0.0.0.0 --port {PORT}
```

## Endpoints

### Health Check

```markdown
curl -X GET http://localhost:{PORT}/healthcheck
```

### Get all todos

```markdown
curl -X GET http://localhost:{PORT}/api/v1/todos
```

### Filter todos

```markdown
curl -X GET http://localhost:{PORT}/api/v1/todos?status=completed
```

### Get a todo

```markdown
curl -X GET http://localhost:{PORT}/api/v1/todos/{pk}
```

### Add a todo

```markdown
curl -X POST http://localhost:{PORT}/api/v1/todos -d '{"title": "Learn FastAPI"}'
```

### Complete a todo

```markdown
curl -X POST http://localhost:{PORT}/api/v1/todos/{pk}
```

### Update a todo

```markdown
curl -X PUT http://localhost:{PORT}/api/v1/todos/{pk} -d '{"title": "Learn FastAPI", "status": "doing"}'
```

### Delete a todo

```markdown
curl -X DELETE http://localhost:{PORT}/api/v1/todos/{pk}
```