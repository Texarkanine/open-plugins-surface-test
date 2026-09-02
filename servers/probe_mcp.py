# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp",
# ]
# ///
"""M1 probe MCP server: exposes probe_hello fingerprint tool."""


def format_probe_hello(name: str) -> str:
    """Return the observation fingerprint for the given name."""
    return f"MCP-OBSERVED-{name}"


def main() -> None:
    """Launch the FastMCP stdio server with the probe_hello tool."""
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("probe-mcp")

    @mcp.tool()
    def probe_hello(name: str) -> str:
        """Return a greeting fingerprint for the given name."""
        return format_probe_hello(name)

    mcp.run()


if __name__ == "__main__":
    main()
