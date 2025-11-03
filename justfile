# Install dependencies
install:
    uv sync

# Run the FastAPI server
dev:
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run the FastAPI server (production mode)
run:
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Format code
fmt:
    uv run ruff format .

# Lint code
lint:
    uv run ruff check .

