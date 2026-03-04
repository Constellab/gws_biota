import reflex as rx
from gws_ai_toolkit._app.ai_chat import (
    AppConfigState,
)
from gws_reflex_main import register_gws_reflex_app

from .biota_chat.biota_app_page_layout import page_layout_component
from .biota_chat.biota_chat_component import biota_chat_component
from .biota_chat.biota_chat_state import BiotaChatState
from .custom_states import CustomAppConfigState

AppConfigState.set_config_state_class_type(CustomAppConfigState)

app = register_gws_reflex_app()


@rx.page(route="/")
def index():
    """Main chat page with sidebar (new conversation)."""
    return page_layout_component(
        content=biota_chat_component(),
    )


@rx.page(route="/chat/[conversation_id]", on_load=BiotaChatState.load_conversation_from_url)
def chat_with_conversation():
    """Chat page for an existing conversation loaded from URL."""
    return page_layout_component(
        content=biota_chat_component(),
    )
