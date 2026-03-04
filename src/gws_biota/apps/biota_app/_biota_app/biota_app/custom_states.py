import reflex as rx
from gws_ai_toolkit._app.ai_chat import (
    AppConfigState,
    AppConfigStateConfig,
    SidebarHistoryListState,
)
from gws_reflex_main import ReflexMainState

from .biota_chat.biota_chat_state import (
    BiotaChatState,
)


class CustomAppConfigState(AppConfigState, rx.State):
    async def _get_config(self) -> AppConfigStateConfig:
        base_state = await self.get_state(ReflexMainState)
        params = await base_state.get_params()
        return AppConfigStateConfig(
            configuration_file_path=params.get("configuration_file_path", ""),
            chat_app_name=params.get("chat_app_name", "biota_agent"),
        )


class CustomHistoryState(SidebarHistoryListState, rx.State):
    def get_active_conversation_id(self) -> str | None:
        """Extract the active conversation ID from the current URL."""
        return self.conversation_id

    @rx.event
    async def select_conversation(self, conversation_id: str, mode: str):
        """Navigate to the conversation page."""
        return rx.redirect(f"/chat/{conversation_id}")

    @rx.event
    async def start_new_chat(self):
        """Start a new chat by navigating to the home page."""
        biota_state = await self.get_state(BiotaChatState)
        biota_state.clear_chat()
        return rx.redirect("/")
