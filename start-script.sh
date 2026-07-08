#!/bin/sh
# Entry point used by container platforms (e.g. SciLifeLab Serve) that invoke
# ./start-script.sh instead of the Docker CMD.
#
# Honours MCP_TRANSPORT / HOST / PORT (see server.py). The platform typically
# injects PORT; we default it to 8000 to match the Dockerfile's EXPOSE.
set -e

export MCP_TRANSPORT="${MCP_TRANSPORT:-streamable-http}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"

exec python -m echa_mcp
