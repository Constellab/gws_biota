import reflex as rx
from gws_ai_toolkit._app.ai_chat import ChatConfig, chat_input_component


def biota_empty_chat_component(config: ChatConfig) -> rx.Component:
    """Custom empty chat component for the Biota chat page.

    Displays a centered layout with the Constellab logo, a title,
    a subtitle, and the chat input field directly below.
    """
    return rx.vstack(
        rx.box(flex="1"),
        # Logo
        rx.image(
            src="/constellab-logo.svg",
            width="72px",
            height="72px",
        ),
        # Title
        rx.heading(
            "Biota Chat",
            size="6",
            weight="bold",
            text_align="center",
        ),
        # Subtitle
        rx.text(
            "Ask questions about biological databases",
            size="3",
            color="gray",
            text_align="center",
            max_width="380px",
        ),
        # Chat input
        rx.box(
            chat_input_component(config),
            width="100%",
            max_width="800px",
            margin="auto",
        ),
        rx.box(flex="2"),
        align="center",
        width="100%",
        flex="1",
        spacing="4",
    )
