import reflex as rx
from gws_ai_toolkit._app.ai_chat import chat_history_sidebar_list
from gws_reflex_main import main_component, page_sidebar_component, sidebar_header_component

from ..custom_states import CustomHistoryState


def page_layout_component(content: rx.Component) -> rx.Component:
    """Standard page layout with sidebar for the RAG app.

    Wraps the given content with the shared sidebar containing
    app branding, New Chat button, and conversation history.

    :param content: The main page content component.
    :param state: The SidebarHistoryListState subclass providing start_new_chat and select_conversation.
    :param sidebar_width: Width of the sidebar.
    :return: The page layout component.
    """
    return main_component(
        page_sidebar_component(
            sidebar_content=_sidebar_content(),
            content=content,
            sidebar_width="300px",
        )
    )


def _sidebar_content() -> rx.Component:
    """Sidebar content for the RAG app pages.

    Contains app branding, New Chat button, and conversation history list.

    """
    return rx.vstack(
        # App branding
        sidebar_header_component(
            title="Bio navigator",
            subtitle="By Constellab",
            logo_src="/constellab-logo.svg",
            margin_bottom="1rem",
        ),
        # New Chat button
        rx.box(
            rx.button(
                rx.icon("plus", size=16),
                "New Chat",
                on_click=CustomHistoryState.start_new_chat,
                width="100%",
                size="2",
            ),
            padding="0 1rem 1rem 1rem",
            width="100%",
        ),
        # Conversation history list (takes remaining space)
        rx.box(
            chat_history_sidebar_list(state=CustomHistoryState),
            flex="1",
            min_height="0",
            overflow_y="auto",
            width="100%",
            padding_inline="1rem",
        ),
        width="100%",
        height="100%",
        spacing="0",
    )
