ECHA CHEM MCP Server
====================

An MCP server built with [FastMCP](https://pypi.org/project/fastmcp/) that
exposes regulatory chemical hazard data from the **ECHA CHEM** database
(European Chemicals Agency, <https://chem.echa.europa.eu>) as MCP tools.

It covers substance identity, REACH registration dossiers, CLP notifications,
harmonised (Annex VI) classifications, PBT assessments, and toxicology /
ecotoxicology study data. All tools are keyed on an **ECHA substance index**
(e.g. `100.000.002` for Formaldehyde).


Repository layout
-----------------
Root — server surface and packaging:
- `server.py` — MCP server definition; registers the tools and resources.
- `tools.py` — thin, well-documented async tool wrappers (the MCP tools).
- `__main__.py` — entry point so `python -m echa_mcp` launches the server.
- `__init__.py` — package marker.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — container recipe for running the server.

`utils/` — implementation details behind the tools:
- `echa_client.py` — async httpx client over the ECHA CHEM HTTP endpoints.
- `substance.py`, `substance_id_resolve.py`, `clp_clf.py`,
  `harmonised_clf.py`, `reach_clf.py`, `toxicology.py` — endpoint logic per
  data domain.
- `parser.py` — dossier HTML parsing + GHS hazard-category → H-code mapping.


Prerequisites
-------------
- Python 3.10+ recommended.
- `pip` for dependency installation.


Running locally
---------------
From the **parent** directory of `echa_mcp/`:

```bash
pip install -r echa_mcp/requirements.txt
python -m echa_mcp
```

The server reads three environment variables:

| Variable        | Default           | Notes                                    |
|-----------------|-------------------|------------------------------------------|
| `MCP_TRANSPORT` | `streamable-http` | `streamable-http`, `http`, `sse`, `stdio` |
| `HOST`          | `0.0.0.0`         | ignored for `stdio`                      |
| `PORT`          | `8000`            | ignored for `stdio`                      |
| `MCP_HOST_ORIGIN_PROTECTION` | `false` | FastMCP 3.x rejects unknown `Host` headers with HTTP 421 ("Misdirected Request"). Left off so the endpoint works behind a reverse proxy. |
| `MCP_ALLOWED_HOSTS` | *(unset)* | Comma-separated Host allowlist, used only when protection is `true` (e.g. `echa-chem.serve.scilifelab.se`). |

> **Deploying behind a reverse proxy (e.g. SciLifeLab Serve):** FastMCP 3.x's
> Host/Origin guard returns `421 Misdirected Request` when the public hostname
> isn't on its allowlist. This server disables the guard by default. To keep it
> on instead, set `MCP_HOST_ORIGIN_PROTECTION=true` and
> `MCP_ALLOWED_HOSTS=<your-domain>`.

For a local stdio client (e.g. Claude Desktop), run with:

```bash
MCP_TRANSPORT=stdio python -m echa_mcp
```


Running with Docker
-------------------
Build and run (from inside `echa_mcp/`):

```bash
docker build -t echa-mcp .
docker run --rm -p 8000:8000 echa-mcp
```

The server listens on `http://localhost:8000/mcp` (streamable-http).


Connecting a client
--------------------
Streamable-HTTP endpoint: `http://localhost:8000/mcp`

Example Claude Code / MCP client config for a stdio launch:

```json
{
  "mcpServers": {
    "echa": {
      "command": "python",
      "args": ["-m", "echa_mcp"],
      "env": { "MCP_TRANSPORT": "stdio" }
    }
  }
}
```


Available tools
---------------
- `echa_resolve_substance_index` — resolve a name/CAS/EC to a single best substance index (recommended entry point).
- `echa_search_substances` — list all substance matches for a name/CAS/EC.
- `echa_get_substance_info` — CAS/EC numbers, names, IUPAC name, formula.
- `echa_list_dossiers` — REACH registration dossiers for a substance.
- `echa_get_clp_classification` — CLP notifications (industry self-classification).
- `echa_get_harmonised_classification` — official EU Annex VI classification.
- `echa_get_reach_ghs` — GHS classification from the REACH dossier (Section 2.1).
- `echa_get_reach_pbt` — PBT / vPvB assessment (Section 2.3).
- `echa_get_toxicology_summary` — toxicology summaries + DN(M)ELs (fast).
- `echa_get_toxicology_studies` — individual toxicology study records (filterable).
- `echa_get_toxicology_full` — complete toxicology data (slow).
- `echa_get_ecotoxicology_data` — environmental fate / ecotoxicology (Sections 5 & 6).

Resources
---------
- `echa://reference/hcode-mapping` — GHS hazard-category → H-code table (Markdown).
- `echa://reference/hcode-mapping.json` — same mapping as JSON.
