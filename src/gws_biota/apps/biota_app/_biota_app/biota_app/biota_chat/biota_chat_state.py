"""
Biota Chat State
================

Reflex state for the Biota database chat, extending ConversationChatStateBase.
"""

import os

import reflex as rx
from gws_ai_toolkit._app.ai_chat import ConversationChatStateBase
from gws_ai_toolkit.models.chat.conversation.base_chat_conversation import (
    BaseChatConversation,
    BaseChatConversationConfig,
)
from gws_reflex_main import ReflexMainState

from gws_biota.ai.biota_agent_ai import BiotaAgentAi

from .biota_chat_conversation import BiotaChatConversation


class BiotaChatState(ConversationChatStateBase, rx.State):
    """State for the Biota database chat interface.

    Provides a chat UI where users can query the Biota biological database
    through an AI agent with function-calling tools.
    """

    # UI configuration
    title: str = "Biota Database Explorer"
    placeholder_text: str = "Ask about enzymes, compounds, reactions..."
    empty_state_message: str = "Ask me anything about the Biota biological database"

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

        biota_agent = BiotaAgentAi(
            openai_api_key=api_key,
            model="gpt-4o",
            temperature=0.3,
        )

        main_state = await self.get_state(ReflexMainState)
        user = await main_state.get_current_user()

        config = BaseChatConversationConfig(
            "biota_agent",
            store_conversation_in_db=False,
            user=user.to_dto() if user else None,
        )

        conversation = BiotaChatConversation(config, biota_agent)
        conversation.debug_mode = self.debug_mode
        return conversation

    @rx.event
    def toggle_debug_mode(self):
        """Toggle debug mode on/off. Applies to both new and existing conversations."""
        self.debug_mode = not self.debug_mode
        if self._conversation and isinstance(self._conversation, BiotaChatConversation):
            self._conversation.debug_mode = self.debug_mode

    @rx.event
    async def download_csv(self, file_path: str, file_name: str):
        """Trigger a browser download for an exported CSV file.

        Args:
            file_path: Absolute path to the CSV file on disk.
            file_name: Filename to use for the download.
        """
        if not os.path.isfile(file_path):
            yield rx.toast.error("CSV file no longer available.")
            return
        with open(file_path, "rb") as f:
            file_data = f.read()
        yield rx.download(data=file_data, filename=file_name)
