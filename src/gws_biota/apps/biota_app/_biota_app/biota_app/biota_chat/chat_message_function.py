"""
Chat Message Function Types
============================

Custom chat message types for debug mode: function calls and function results.
"""

import json
from typing import Literal

from gws_ai_toolkit import ChatMessageBase, ChatMessageText


class ChatMessageFunctionCall(ChatMessageBase):
    """Chat message representing a function call made by the AI agent.

    Attributes:
        type: Fixed as "function-call".
        function_name: Name of the function being called.
        arguments_json: JSON string of the function arguments.
    """

    type: Literal["function-call"] = "function-call"
    role: Literal["assistant"] = "assistant"
    function_name: str
    arguments_json: str

    @staticmethod
    def from_event(function_name: str, arguments: dict) -> "ChatMessageFunctionCall":
        return ChatMessageFunctionCall(
            function_name=function_name,
            arguments_json=json.dumps(arguments, indent=2, default=str),
        )

    def to_front_dto(self) -> ChatMessageText:
        content = f"**Function call:** `{self.function_name}`\n```json\n{self.arguments_json}\n```"
        return ChatMessageText(
            id=self.id,
            external_id=self.external_id,
            user=self.user,
            content=content,
        )


class ChatMessageFunctionResult(ChatMessageBase):
    """Chat message representing the result of a function call.

    Attributes:
        type: Fixed as "function-result".
        function_name: Name of the function that was called.
        result_preview: Truncated preview of the function result.
    """

    type: Literal["function-result"] = "function-result"
    role: Literal["assistant"] = "assistant"
    function_name: str
    result_preview: str

    @staticmethod
    def from_result(
        function_name: str, result: str, max_length: int = 500
    ) -> "ChatMessageFunctionResult":
        preview = result if len(result) <= max_length else result[:max_length] + "..."
        return ChatMessageFunctionResult(
            function_name=function_name,
            result_preview=preview,
        )

    def to_front_dto(self) -> ChatMessageText:
        content = f"**Function result:** `{self.function_name}`\n```\n{self.result_preview}\n```"
        return ChatMessageText(
            id=self.id,
            external_id=self.external_id,
            user=self.user,
            content=content,
        )
