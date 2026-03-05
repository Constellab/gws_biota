"""
Biota Agent AI
==============

AI agent for querying the Biota biological database using OpenAI function calling.
Wraps the 4 biota_db_tools functions as OpenAI tools.
"""

import json
from collections.abc import Generator

from gws_ai_toolkit.core.agents.base_function_agent_ai import BaseFunctionAgentAi
from gws_ai_toolkit.core.agents.base_function_agent_events import (
    FunctionCallEvent,
    FunctionErrorEvent,
    UserQueryTextEvent,
)
from gws_core import BaseModelDTO
from pydantic import Field

from .biota_agent_ai_events import (
    BiotaAgentEvent,
    ExportResultEvent,
    QueryResultEvent,
    SchemaResultEvent,
    StatisticsResultEvent,
)
from .biota_chat_config import BiotaChatConfig
from .biota_db_tools import export_to_csv, get_database_statistics, get_schema, query


class QueryConfig(BaseModelDTO):
    """Configuration for the query tool."""

    sql: str = Field(
        description="A SELECT query to execute against the Biota database. "
        "Only SELECT queries are allowed. Always include relevant columns rather than SELECT *."
    )
    limit: int = Field(
        default=10,
        description="Max rows to return (default 10, maximum 20). "
        "Does not apply to aggregate queries (COUNT, SUM, etc.).",
    )


class ExportToCsvConfig(BaseModelDTO):
    """Configuration for the export_to_csv tool."""

    sql: str = Field(
        description="A SELECT query. Should include specific columns (avoid SELECT *). "
        "All matching rows are written to the file (no row limit)."
    )
    filename: str | None = Field(
        default=None,
        description="Optional CSV filename (without path). If not provided, one is auto-generated. "
        "The file is saved to /lab/user/data/.",
    )


class BiotaAgentAi(BaseFunctionAgentAi[BiotaAgentEvent, UserQueryTextEvent]):
    """AI agent for exploring the Biota biological database.

    Uses OpenAI function calling with 4 tools:
    get_schema, query, export_to_csv, get_database_statistics.
    """

    _system_prompt: str

    def __init__(
        self,
        openai_api_key: str,
        model: str,
        temperature: float,
        system_prompt: str | None = None,
        skip_success_response: bool = False,
    ):
        super().__init__(
            openai_api_key, model, temperature, skip_success_response=skip_success_response
        )
        self._system_prompt = system_prompt or BiotaChatConfig().system_prompt

    def _get_tools(self) -> list[dict]:
        """Get tools configuration for OpenAI."""
        return [
            {
                "type": "function",
                "name": "get_schema",
                "description": "Returns the complete database schema: all tables, columns with types, "
                "foreign key relationships, and common SQL join patterns as examples. "
                "Call this once at the start of a conversation to understand the database structure.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
            {
                "type": "function",
                "name": "query",
                "description": "Execute a read-only SQL SELECT query against the Biota database. "
                "Returns results as a list of row dictionaries. Use for exploration, counts, "
                "and answering user questions. For large exports, use export_to_csv instead.",
                "parameters": QueryConfig.model_json_schema(),
            },
            {
                "type": "function",
                "name": "export_to_csv",
                "description": "Execute a SQL SELECT query and write ALL results to a CSV file. "
                "Use this when the user requests large datasets, full exports, or complete lists. "
                "There is no row limit — all matching rows are written to the file.",
                "parameters": ExportToCsvConfig.model_json_schema(),
            },
            {
                "type": "function",
                "name": "get_database_statistics",
                "description": "Get an overview of the Biota database: total counts per entity type "
                "(enzymes, proteins, compounds, reactions, pathways, taxa, BTO tissues, GO terms, etc.). "
                "Use this to understand what data is available before writing queries.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        ]

    def _handle_function_call(
        self, function_call_event: FunctionCallEvent, user_query: UserQueryTextEvent
    ) -> Generator[BiotaAgentEvent, None, None]:
        """Handle function call event by dispatching to the appropriate biota_db_tools function."""
        call_id = function_call_event.call_id
        response_id = function_call_event.response_id
        function_name = function_call_event.function_name
        arguments = function_call_event.arguments

        try:
            if function_name == "get_schema":
                result = get_schema()
                yield SchemaResultEvent(
                    schema_text=result,
                    call_id=call_id,
                    response_id=response_id,
                    function_response=result,
                    agent_id=self.id,
                )

            elif function_name == "query":
                sql = arguments.get("sql", "")
                limit = arguments.get("limit", 10)
                result = query(sql, limit=limit)
                yield QueryResultEvent(
                    query_data=result,
                    call_id=call_id,
                    response_id=response_id,
                    function_response=json.dumps(result, default=str),
                    agent_id=self.id,
                )

            elif function_name == "export_to_csv":
                sql = arguments.get("sql", "")
                filename = arguments.get("filename", None)
                result = export_to_csv(sql, filename=filename)
                yield ExportResultEvent(
                    export_data=result,
                    call_id=call_id,
                    response_id=response_id,
                    function_response=json.dumps(result, default=str),
                    agent_id=self.id,
                )

            elif function_name == "get_database_statistics":
                result = get_database_statistics()
                yield StatisticsResultEvent(
                    statistics_data=result,
                    call_id=call_id,
                    response_id=response_id,
                    function_response=json.dumps(result, default=str),
                    agent_id=self.id,
                )

            else:
                yield FunctionErrorEvent(
                    message=f"Unknown function: {function_name}",
                    call_id=call_id,
                    response_id=response_id,
                    agent_id=self.id,
                )

        except Exception as e:
            yield FunctionErrorEvent(
                message=str(e),
                call_id=call_id,
                response_id=response_id,
                agent_id=self.id,
            )

    def _get_ai_instruction(self, user_query: UserQueryTextEvent) -> str:
        """Create the system prompt for the biological database expert."""
        return self._system_prompt
