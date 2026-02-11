FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code

ENV PATH="/code/.venv/bin:$PATH"

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock .python-version* ./

RUN uv sync --locked

# Copy entire project
COPY . .

# Default entrypoint (change if needed)
ENTRYPOINT ["sh", "-c", "python scripts/data_loader.py && python scripts/load_to_bq.py"]