"""
Biota Chat State
================

Reflex state for the Biota database chat, extending ConversationChatStateBase.
"""

import os
from typing import cast

import reflex as rx
from gws_ai_toolkit import (
    BaseChatConversation,
    BaseChatConversationConfig,
    ChatConversation,
    ChatConversationService,
)
from gws_ai_toolkit._app.ai_chat import AppConfigState, ConversationChatStateBase, HistoryState
from gws_biota.ai.biota_agent_ai import BiotaAgentAi
from gws_biota.ai.chat_message_csv_export import ChatMessageCsvExport
from gws_reflex_main import ReflexMainState

from .biota_chat_conversation import BiotaChatConversation
from .biota_config_state import BiotaConfigState


class BiotaChatState(ConversationChatStateBase, rx.State):
    """State for the Biota database chat interface.

    Provides a chat UI where users can query the Biota biological database
    through an AI agent with function-calling tools.
    """

    # Debug mode: when enabled, intermediate reasoning and function calls are shown in the chat
    debug_mode: bool = False

    async def _create_conversation(self) -> BaseChatConversation:
        """Create a new BiotaChatConversation instance.

        Returns:
            BaseChatConversation: A configured BiotaChatConversation.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is not set")

        biota_config_state = await self.get_state(BiotaConfigState)
        biota_config = await biota_config_state.get_config()

        self.placeholder_text = biota_config.placeholder_text

        biota_agent = BiotaAgentAi(
            openai_api_key=api_key,
            model=biota_config.model,
            temperature=biota_config.temperature,
            system_prompt=biota_config.system_prompt,
        )

        main_state = await self.get_state(ReflexMainState)
        user = await main_state.get_current_user()

        app_config_state = await AppConfigState.get_instance(self)
        chat_app_name = await app_config_state.get_chat_app_name()

        config = BaseChatConversationConfig(
            chat_app_name or "biota_agent",
            store_conversation_in_db=True,
            user=user.to_dto() if user else None,
        )

        conversation = BiotaChatConversation(config, biota_agent)
        conversation.debug_mode = self.debug_mode
        return conversation

    async def _restore_conversation(self, conversation_id: str) -> None:
        """Restore a BiotaChatConversation for an existing conversation."""
        conversation = await self._create_conversation()

        main_state = await self.get_state(ReflexMainState)
        with await main_state.authenticate_user():
            db_conversation: ChatConversation = ChatConversation.get_by_id_and_check(
                conversation_id
            )
            conversation._conversation_id = conversation_id
            conversation._external_conversation_id = db_conversation.external_conversation_id

            conversation_service = ChatConversationService()
            conversation.chat_messages = conversation_service.get_messages_of_conversation(
                conversation_id
            )

        self._conversation = conversation

    async def _after_conversation_updated(self) -> rx.event.EventSpec | None:
        """Refresh the sidebar conversation list and update URL after a message is sent."""
        async with self:
            history_state = await self.get_state(HistoryState)
            await history_state.load_conversations()

        if self._conversation and self._conversation._conversation_id:
            conversation_id = self._conversation._conversation_id
            return rx.call_script(
                f'window.history.replaceState({{}}, "", "/chat/{conversation_id}")'
            )
        return None

    @rx.event
    async def load_conversation_from_url(self) -> None:
        """Handle page load for /chat/[conversation_id] route."""
        conversation_id = self.conversation_id

        if not conversation_id:
            return

        await self.load_conversation(conversation_id)

    @rx.event
    def toggle_debug_mode(self):
        """Toggle debug mode on/off. Applies to both new and existing conversations."""
        self.debug_mode = not self.debug_mode
        if self._conversation and isinstance(self._conversation, BiotaChatConversation):
            self._conversation.debug_mode = self.debug_mode

    @rx.event
    async def download_csv(self, message_id: str):
        """Trigger a browser download for an exported CSV file.

        Args:
            message_id: ID of the ChatMessageCsvExport message in the conversation.
        """
        if not self._conversation:
            yield rx.toast.error("No active conversation.")
            return

        message: ChatMessageCsvExport = cast(
            ChatMessageCsvExport,
            next(
                (
                    msg
                    for msg in self._conversation.chat_messages
                    if msg.id == message_id and isinstance(msg, ChatMessageCsvExport)
                ),
                None,
            ),
        )

        if not message:
            yield rx.toast.error("CSV export message not found.")
            return

        if not os.path.isfile(message.file_path):
            yield rx.toast.error("CSV file no longer available.")
            return

        with open(message.file_path, "rb") as f:
            file_data = f.read()
        yield rx.download(data=file_data, filename=message.file_name)
