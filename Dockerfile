# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MCP_TRANSPORT=streamable-http \
    HOST=0.0.0.0 \
    PORT=8000 \
    # FastMCP 3.x Host/Origin guard is off by default here so the endpoint works
    # behind a reverse proxy (e.g. SciLifeLab Serve) without returning HTTP 421.
    MCP_HOST_ORIGIN_PROTECTION=false

# Set working directory (the package `echa_mcp` lives directly beneath it)
WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy the package source into /app/echa_mcp
COPY . /app/echa_mcp/

# Expose the start script at the working directory for platforms that invoke
# ./start-script.sh (e.g. SciLifeLab Serve) instead of the Docker CMD.
RUN cp /app/echa_mcp/start-script.sh /app/start-script.sh \
    && chmod +x /app/start-script.sh

# Expose port for HTTP / streamable-http server
EXPOSE 8000

# Run the MCP server. python -m echa_mcp -> echa_mcp/__main__.py.
# Platforms that override this with ./start-script.sh get the same behaviour.
CMD ["./start-script.sh"]
