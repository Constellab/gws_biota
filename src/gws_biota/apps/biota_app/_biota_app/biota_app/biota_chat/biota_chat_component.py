"""
Biota Chat Component
====================

UI component that wires BiotaChatState to the chat_component
with custom renderers for CSV export and debug messages.
"""

import reflex as rx
from gws_ai_toolkit._app.ai_chat import ChatConfig, chat_component

from .biota_chat_state import BiotaChatState
from .chat_message_csv_export import ChatMessageCsvExport
from .chat_message_function import ChatMessageFunctionCall, ChatMessageFunctionResult


def _csv_export_message_content(message: ChatMessageCsvExport) -> rx.Component:
    """Render a CSV export message with a download button."""
    return rx.button(
        rx.hstack(
            rx.icon("file-down", size=20),
            rx.vstack(
                rx.text(
                    message.file_name,
                    font_weight="600",
                    font_size="14px",
                ),
                rx.text(
                    message.row_count.to(str) + " rows exported",
                    font_size="12px",
                    color="var(--gray-11)",
                ),
                spacing="0",
                align_items="flex-start",
            ),
            rx.spacer(),
            rx.icon("download", size=16, color="var(--gray-11)"),
            spacing="3",
            align_items="center",
            width="100%",
        ),
        on_click=BiotaChatState.download_csv(message.file_path, message.file_name),
        variant="soft",
        size="3",
        width="100%",
        cursor="pointer",
        justify_content="start",
        height="60px",
    )


def _function_call_message_content(message: ChatMessageFunctionCall) -> rx.Component:
    """Render a function call debug message."""
    return rx.box(
        rx.hstack(
            rx.icon("play", size=14, color="var(--amber-11)"),
            rx.text(
                "Called ",
                rx.text(message.function_name, font_weight="600", as_="span"),
                font_size="13px",
                color="var(--gray-11)",
            ),
            spacing="2",
            align_items="center",
        ),
        rx.code_block(
            message.arguments_json,
            language="json",
            font_size="12px",
        ),
        padding="8px 12px",
        border_radius="8px",
        background="var(--amber-2)",
        border="1px solid var(--amber-6)",
        width="100%",
    )


def _function_result_message_content(message: ChatMessageFunctionResult) -> rx.Component:
    """Render a function result debug message."""
    return rx.box(
        rx.hstack(
            rx.icon("check", size=14, color="var(--green-11)"),
            rx.text(
                "Result from ",
                rx.text(message.function_name, font_weight="600", as_="span"),
                font_size="13px",
                color="var(--gray-11)",
            ),
            spacing="2",
            align_items="center",
        ),
        rx.code_block(
            message.result_preview,
            language="json",
            font_size="12px",
        ),
        padding="8px 12px",
        border_radius="8px",
        background="var(--green-2)",
        border="1px solid var(--green-6)",
        width="100%",
    )


def _header_buttons(state: BiotaChatState) -> list[rx.Component]:
    """Header buttons including debug toggle and clear chat."""
    return [
        rx.tooltip(
            rx.button(
                rx.icon("bug", size=16),
                on_click=BiotaChatState.toggle_debug_mode,
                variant=rx.cond(state.debug_mode, "solid", "ghost"),
                color_scheme=rx.cond(state.debug_mode, "amber", "gray"),
                size="2",
                cursor="pointer",
            ),
            content=rx.cond(
                state.debug_mode,
                "Debug mode ON",
                "Debug mode OFF",
            ),
        ),
        rx.button(
            rx.icon("refresh-cw", size=16),
            "New chat",
            on_click=state.clear_chat,
            variant="ghost",
            size="2",
            cursor="pointer",
        ),
    ]


def biota_chat_component() -> rx.Component:
    return chat_component(
        ChatConfig(
            state=BiotaChatState,
            # header_buttons=_header_buttons,
            custom_chat_messages={  # type: ignore
                "csv-export": _csv_export_message_content,
                "function-call": _function_call_message_content,
                "function-result": _function_result_message_content,
            },
        )
    )
