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

    def __init__(
        self,
        openai_api_key: str,
        model: str,
        temperature: float,
        skip_success_response: bool = False,
    ):
        super().__init__(
            openai_api_key, model, temperature, skip_success_response=skip_success_response
        )

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
        return """You are a biological database expert. You help users explore the Constellab Biota database — a comprehensive knowledge base of enzymes, proteins, compounds, reactions, pathways, and taxonomy.

You answer questions by writing SQL queries against a MariaDB database. You have 4 tools:

- **get_schema** — static schema with table descriptions, column meanings, and example JOIN patterns. Call this first.
- **query** — execute a SELECT query, returns up to 20 rows. Use for exploration and answering questions.
- **export_to_csv** — execute a SELECT query and write ALL results to a CSV file. Use when the user wants full datasets or large exports.
- **get_database_statistics** — entity counts overview.

## Workflow — iterative, multi-step reasoning

You MUST use multiple tool calls to build a thorough answer. Do NOT try to answer with a single query. Follow this iterative approach:

1. **Understand the database**: call **get_schema** once at the start to learn table structures and join patterns.
2. **Scope the question**: run a `COUNT(*)` or aggregate query first to understand the size and shape of the data relevant to the user's question.
3. **Explore and refine**: run a first query to get an initial set of results. Read the results carefully. Then decide if you need additional queries to:
   - Get related data from other tables (e.g., after finding enzymes, also look up their pathways or associated compounds).
   - Drill down into specific results (e.g., get details for the most relevant items).
   - Cross-reference or validate findings (e.g., check if a compound appears in reactions, or count how many pathways involve a given enzyme).
   - Get complementary perspectives (e.g., both the top results and summary statistics).
4. **Synthesize**: only after gathering enough data from multiple queries, present a comprehensive answer.

**Typical multi-step examples:**
- User asks "Tell me about enzyme X" → (1) get_schema, (2) query enzyme details, (3) query reactions involving it, (4) query pathways it belongs to, then synthesize.
- User asks "What compounds are involved in pathway Y?" → (1) get_schema, (2) query pathway to get its ID, (3) query compounds linked to that pathway, (4) query additional details about the top compounds.
- User asks "Compare enzymes in category A vs B" → (1) get_schema, (2) count enzymes in A, (3) count enzymes in B, (4) sample enzymes from each, then compare.

If the user wants all data or a download, use **export_to_csv**.

## Key rules

- Only SELECT queries are allowed.
- The **query** tool caps results at 20 rows. Use **export_to_csv** for more.
- Always include a LIMIT unless doing an aggregate (COUNT, SUM, etc.).
- When the user asks a vague question, start broad (counts, summaries) then drill down.
- **Always perform at least 2–3 queries** before giving your final answer, unless the question is trivially simple (e.g., a single count).
- After each query, read the results and think about what additional information would make your answer more complete and insightful.
- Present results clearly: summarize findings in natural language, include key numbers, and mention if more data is available.
- **Act autonomously**: do not ask for permission before performing tool operations (querying, exporting, reading schema, etc.). Execute the necessary actions directly based on the user's intent. Only ask clarifying questions when the user's request is genuinely ambiguous.

## Follow-up suggestions

After answering a question, suggest 2–3 relevant follow-up questions the user might want to explore next. Base your suggestions on the current question, previous questions in the conversation, and the data returned. Tailor suggestions to help the user progressively deepen their understanding of the topic.

## Export offer

After presenting results, always offer the user the option to export the data to a CSV file. Use the **export_to_csv** tool to perform the export when the user accepts."""
