from mcp.server.fastmcp import FastMCP


def init_gws_core():
    from gws_core_loader import load_gws_core

    load_gws_core()

    from gws_core.manage import AppManager

    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="INFO")


init_gws_core()

from gws_biota import Enzyme

mcp = FastMCP(
    "data-platform",
    instructions=("This server provides access to tools to request Constellab biota database."),
)


@mcp.tool(description="Find an enzyme by its EC number")
def find_enzyme(ec_number: str) -> Enzyme:
    """Find an enzyme by its EC number.

    This tool allows you to query the database for an enzyme
    using its EC number.
    """

    return Enzyme.select().where(Enzyme.ec_number == ec_number).first()


mcp.run(transport="stdio")
