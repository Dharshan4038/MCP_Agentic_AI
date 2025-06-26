from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="weather",
    host="0.0.0.0",
    port=8000,
)

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")

def format_alert(feature:dict) -> str:
    props = feature["properties"]
    return f"""
        Event: {props.get("event", "Unknown")}
        Area: {props.get("areaDesc", "Unknown")}
        Severity: {props.get("severity", "Unknown")}
        Description: {props.get("description", "No description available")}
        Instruction: {props.get("instruction", "No instruction available")}
    """

@mcp.tool()
async def get_alerts(state: str) -> str:
    """ Get weather alerts for a US state.
    Args:
        state: two-letter US state code (eg: CA, NY, etc.)
    """

    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    
    if not data or "features" not in data:
        return "No alerts found for this state."
    
    if not data["features"]:
        return "No active alerts found for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n-------\n".join(alerts)


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """ Echo a message as a resource."""
    return f"Resource echo: {message}"


if __name__ == "__main__":
    transport = "sse"
    if transport == "stdio":
        print("Starting MCP server with stdio transport...")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Starting MCP server with SSE transport...")
        mcp.run(transport="sse")
    else:
        raise ValueError("Invalid transport. Please choose 'stdio' or 'sse'.")
