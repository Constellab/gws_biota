"""
Chat Message CSV Export
=======================

Custom chat message type for displaying a CSV export result with a download button.
"""

from typing import Literal

from gws_ai_toolkit.models.chat.message.chat_message_base import ChatMessageBase


class ChatMessageCsvExport(ChatMessageBase):
    """Chat message representing a completed CSV export with download capability.

    Attributes:
        type: Fixed as "csv-export" to identify this message type.
        file_path: Absolute path to the generated CSV file on disk.
        file_name: Display name of the CSV file.
        row_count: Number of rows exported.
    """

    type: Literal["csv-export"] = "csv-export"
    role: Literal["assistant"] = "assistant"
    file_path: str
    file_name: str
    row_count: int
