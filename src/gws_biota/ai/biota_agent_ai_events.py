"""
Biota Agent AI Events
=====================

Event types for the BiotaAgentAi, following the PlotlyAgentAi pattern.
"""

from typing import Literal

from gws_ai_toolkit import (
    BaseFunctionAgentEvent,
    FunctionSuccessEvent,
    UserQueryTextEvent,
)


class SchemaResultEvent(FunctionSuccessEvent):
    type: Literal["schema_result"] = "schema_result"
    schema_text: str


class QueryResultEvent(FunctionSuccessEvent):
    type: Literal["query_result"] = "query_result"
    query_data: dict


class ExportResultEvent(FunctionSuccessEvent):
    type: Literal["export_result"] = "export_result"
    export_data: dict


class StatisticsResultEvent(FunctionSuccessEvent):
    type: Literal["statistics_result"] = "statistics_result"
    statistics_data: dict


# Union type for all Biota agent events
BiotaAgentEvent = (
    SchemaResultEvent
    | QueryResultEvent
    | ExportResultEvent
    | StatisticsResultEvent
    | UserQueryTextEvent
    | BaseFunctionAgentEvent
)
