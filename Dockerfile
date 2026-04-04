FROM python:3.13-slim

WORKDIR /app

# Install uv dependency manager extremely quickly using the official astral image strategy
COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /uvx /bin/

# Transfer Python configurations
COPY pyproject.toml uv.lock ./

# Install dependencies directly into the system wrapper leveraging uv
RUN uv sync --frozen

# Transfer source code repository
COPY . .

EXPOSE 5000

ENV PROMETHEUS_MULTIPROC_DIR=/tmp/multiproc
RUN mkdir -p /tmp/multiproc

# Spin up Gunicorn WSGI pointing at run:app to securely launch horizontal bindings
CMD sh -c "rm -rf /tmp/multiproc/* && uv run gunicorn -w 4 -b 0.0.0.0:5000 run:app"
