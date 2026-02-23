import reflex as rx
from gws_reflex_main import main_component, register_gws_reflex_app

from .biota_chat.biota_chat_component import biota_chat_component

app = register_gws_reflex_app()


@rx.page()
def index():
    return main_component(
        rx.box(
            biota_chat_component(),
            padding_top="1em",
            padding_bottom="1em",
            width="100%",
            height="100%",
        )
    )
