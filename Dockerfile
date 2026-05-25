# Use a lightweight Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies without copying the source code first (caching)
RUN uv sync --frozen --no-cache --no-dev

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uv", "run", "python", "-m", "app.main"]
