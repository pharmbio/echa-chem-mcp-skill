"""FastMCP server exposing ECHA CHEM database tools.

Wraps the async tool functions defined in ``tools.py`` as MCP tools and
resources. Run with::

    python -m echa_mcp

Transport, host, and port are controlled by the MCP_TRANSPORT / HOST / PORT
environment variables (defaults: streamable-http on 0.0.0.0:8000).
"""

from __future__ import annotations

import os

import fastmcp
from fastmcp import FastMCP

from . import tools


def _env_flag(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}

# =============================================================================
# MCP SERVER INSTANCE
# =============================================================================

mcp = FastMCP(
    "echa-mcp",
    instructions=(
        "Tools for querying the ECHA CHEM database (European Chemicals Agency) "
        "for regulatory hazard data on chemical substances: substance identity, "
        "REACH registration dossiers, CLP notifications, harmonised (Annex VI) "
        "classifications, PBT assessments, and toxicology / ecotoxicology study "
        "data.\n\n"
        "All tools are keyed on an ECHA substance index (e.g. '100.000.002' for "
        "Formaldehyde). A typical workflow: start with echa_get_substance_info to "
        "confirm identity, then branch to classification (CLP / harmonised) or "
        "hazard-data (toxicology / ecotoxicology) tools as needed. Consult the "
        "echa://reference/hcode-mapping resource to translate GHS hazard "
        "categories into H-statement codes."
    ),
)

# =============================================================================
# TOOL REGISTRATION
#
# The functions in tools.py are already async and carry rich docstrings that
# double as the MCP tool descriptions, so we register them directly under
# stable, namespaced tool names.
# =============================================================================

_TOOLS = [
    ("echa_resolve_substance_index", tools.tool_resolve_substance_index),
    ("echa_search_substances", tools.tool_search_substances),
    ("echa_get_substance_info", tools.tool_get_substance_info),
    ("echa_list_dossiers", tools.tool_list_dossiers),
    ("echa_get_clp_classification", tools.tool_get_clp_classification),
    ("echa_get_harmonised_classification", tools.tool_get_harmonised_classification),
    ("echa_get_reach_ghs", tools.tool_get_reach_ghs),
    ("echa_get_reach_pbt", tools.tool_get_reach_pbt),
    ("echa_get_toxicology_summary", tools.tool_get_toxicology_summary),
    ("echa_get_toxicology_studies", tools.tool_get_toxicology_studies),
    ("echa_get_toxicology_full", tools.tool_get_toxicology_full),
    ("echa_get_ecotoxicology_data", tools.tool_get_ecotoxicology_data),
]

for _name, _fn in _TOOLS:
    mcp.tool(name=_name)(_fn)


# =============================================================================
# RESOURCE REGISTRATION
# =============================================================================

mcp.resource(
    "echa://reference/hcode-mapping",
    name="hcode_mapping_markdown",
    mime_type="text/markdown",
)(tools.resource_hcode_mapping)

mcp.resource(
    "echa://reference/hcode-mapping.json",
    name="hcode_mapping_json",
    mime_type="application/json",
)(tools.resource_hcode_mapping_json)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    run_kwargs = {"transport": transport}
    if transport in {"http", "streamable-http", "sse"}:
        run_kwargs.update({"host": host, "port": port})

        # FastMCP 3.x guards the HTTP endpoint with a Host/Origin allowlist and
        # returns "421 Misdirected Request" for any Host it doesn't recognise
        # (default: localhost only). When deployed behind a reverse proxy such
        # as SciLifeLab Serve the public hostname isn't in that list, so the
        # guard is disabled by default here. Re-enable it with
        # MCP_HOST_ORIGIN_PROTECTION=true and set MCP_ALLOWED_HOSTS to a
        # comma-separated allowlist (e.g. "echa-chem.serve.scilifelab.se").
        protect = _env_flag("MCP_HOST_ORIGIN_PROTECTION", False)
        allowed = [
            h.strip()
            for h in os.getenv("MCP_ALLOWED_HOSTS", "").split(",")
            if h.strip()
        ]
        # Set on the settings singleton too, so it applies regardless of which
        # code path (kwargs vs. settings fallback) FastMCP consults.
        try:
            fastmcp.settings.http_host_origin_protection = protect
            if allowed:
                fastmcp.settings.http_allowed_hosts = allowed
        except Exception:
            pass
        run_kwargs["host_origin_protection"] = protect
        if allowed:
            run_kwargs["allowed_hosts"] = allowed

    mcp.run(**run_kwargs)


if __name__ == "__main__":
    main()
