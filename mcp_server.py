"""Optional MCP server exposing ClinicalTrials.gov retrieval as a reusable tool.

Run in an isolated MCP environment: `python mcp_server.py`. It uses stdio, so an
MCP-capable client can invoke `search_clinical_trials` without exposing secrets.
"""
from mcp.server.fastmcp import FastMCP
from app import QueryRequest, fetch_studies

mcp = FastMCP("ClinicalTrials.gov Visualization Tools")

@mcp.tool()
async def search_clinical_trials(query: str, condition: str | None = None, drug_name: str | None = None, max_studies: int = 100) -> dict:
    """Retrieve source records from the official ClinicalTrials.gov API, with no generated facts."""
    studies = await fetch_studies(QueryRequest(query=query, condition=condition, drug_name=drug_name, max_studies=max_studies))
    return {"source":"clinicaltrials.gov/api/v2/studies", "count":len(studies), "studies":studies}

if __name__ == "__main__":
    mcp.run(transport="stdio")
