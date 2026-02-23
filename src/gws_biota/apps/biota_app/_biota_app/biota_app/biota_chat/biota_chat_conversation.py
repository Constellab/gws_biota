"""
Biota Chat Conversation
=======================

Bridge between BiotaAgentAi events and chat messages.
Follows the AiTableAgentChatConversation pattern.
"""

import os
from collections.abc import Generator

from gws_ai_toolkit.models.chat.message.chat_message_error import ChatMessageError
from gws_ai_toolkit.models.chat.message.chat_message_types import ChatMessage
from gws_ai_toolkit.models.chat.message.chat_user_message import ChatUserMessageText

from gws_ai_toolkit.models.chat.conversation.base_chat_conversation import (
    BaseChatConversation,
    BaseChatConversationConfig,
)
from gws_ai_toolkit.core.agents.base_function_agent_events import UserQueryTextEvent

from gws_biota.ai.biota_agent_ai import BiotaAgentAi
from gws_biota.ai.biota_agent_ai_events import BiotaAgentEvent

from .chat_message_csv_export import ChatMessageCsvExport
from .chat_message_function import ChatMessageFunctionCall, ChatMessageFunctionResult


class BiotaChatConversation(BaseChatConversation[ChatUserMessageText]):
    """Chat conversation for the Biota database agent.

    Bridges BiotaAgentAi events to chat messages for the Reflex UI.
    """

    biota_agent: BiotaAgentAi
    debug_mode: bool = False

    _current_external_response_id: str | None = None
    _pending_function_call: bool = False

    def __init__(self, config: BaseChatConversationConfig, biota_agent: BiotaAgentAi) -> None:
        super().__init__(
            config,
            mode="biota_agent",
            chat_configuration={
                "model": biota_agent.get_model(),
                "temperature": biota_agent.get_temperature(),
            },
        )
        self.biota_agent = biota_agent
        self._current_external_response_id = None
        self._pending_function_call = False

    def _call_ai_chat(
        self, user_message: ChatUserMessageText
    ) -> Generator[ChatMessage, None, None]:
        """Handle user message by forwarding to the BiotaAgentAi.

        Converts agent events into chat messages for the UI.

        Args:
            user_message: The message from the user.

        Yields:
            ChatMessage: Chat messages for the UI.
        """
        yield user_message

        user_query = UserQueryTextEvent(
            query=user_message.content, agent_id=self.biota_agent.id
        )

        for event in self.biota_agent.call_agent(user_query):
            messages = self._handle_biota_agent_event(event)
            yield from messages

    def _handle_biota_agent_event(self, event: BiotaAgentEvent) -> list[ChatMessage]:  # noqa: PLR0911
        """Handle a single BiotaAgentAi event and return chat messages.

        Args:
            event: The BiotaAgentEvent to handle.

        Returns:
            List of chat messages (empty if no messages to return).
        """
        if event.type == "text_delta":
            message = self.build_current_message(
                event.delta, external_id=self._current_external_response_id
            )
            return [message] if message else []

        if event.type in {"error", "function_error"}:
            error_message = ChatMessageError(
                error=event.message,
                external_id=getattr(event, "response_id", None),
            )
            return [self.save_message(message=error_message)]

        if event.type == "response_created":
            self._pending_function_call = False
            if event.response_id is not None:
                self._current_external_response_id = event.response_id
            return []

        if event.type == "function_call":
            self._pending_function_call = True
            messages: list[ChatMessage] = []
            if self.debug_mode:
                # In debug mode: save the intermediate reasoning text, then show the function call
                closed = self.close_current_message()
                if closed:
                    messages.append(closed)
                call_msg = ChatMessageFunctionCall.from_event(
                    function_name=event.function_name,
                    arguments=event.arguments,
                )
                messages.append(self.save_message(call_msg))
            else:
                # Normal mode: discard intermediate reasoning
                self.current_response_message = None
            return messages

        if event.type == "response_completed":
            self._current_external_response_id = None
            if self._pending_function_call:
                self._pending_function_call = False
                return []
            message = self.close_current_message()
            return [message] if message else []

        # When a CSV export completes, emit a custom message so the UI can show a download button.
        if event.type == "export_result":
            export_data = event.export_data
            file_path = export_data.get("file_path", "")
            if file_path:
                csv_message = ChatMessageCsvExport(
                    file_path=file_path,
                    file_name=os.path.basename(file_path),
                    row_count=export_data.get("row_count", 0),
                )
                return [self.save_message(message=csv_message)]
            return []

        # In debug mode, show function results for all success events
        if self.debug_mode and event.type in {
            "schema_result", "query_result", "statistics_result",
        }:
            result_str = getattr(event, "function_response", "")
            result_msg = ChatMessageFunctionResult.from_result(
                function_name=event.type.replace("_result", ""),
                result=str(result_str),
            )
            return [self.save_message(result_msg)]

        # Other function success events are silently consumed —
        # the base loop feeds them back to OpenAI automatically.
        return []
