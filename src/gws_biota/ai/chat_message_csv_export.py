"""
Chat Message CSV Export
=======================

Custom chat message type for displaying a CSV export result with a download button.
"""

import os
import shutil


from gws_ai_toolkit import ChatConversation, ChatMessageBase, ChatMessageModel


@ChatMessageBase.register_message_type
class ChatMessageCsvExport(ChatMessageBase):
    """Chat message representing a completed CSV export with download capability.

    Attributes:
        type: Fixed as "csv-export" to identify this message type.
        file_path: Absolute path to the generated CSV file on disk.
        file_name: Display name of the CSV file.
        row_count: Number of rows exported.
    """

    message_type: str = "csv-export"
    role: str = "assistant"
    file_path: str = ""
    file_name: str = ""
    row_count: int = 0

    def fill_from_model(self, chat_message: "ChatMessageModel") -> None:
        data = chat_message.data or {}
        self.file_name = data.get("file_name", "")
        self.row_count = data.get("row_count", 0)

        file_path = chat_message.get_filepath_if_exists()
        self.file_path = file_path or ""

    def to_chat_message_model(self, conversation: "ChatConversation") -> "ChatMessageModel":

        message = ChatMessageModel.build_message(
            conversation=conversation,
            role=self.role,
            type_=self.message_type,
            data={"file_name": self.file_name, "row_count": self.row_count},
        )

        if self.file_path and os.path.isfile(self.file_path):
            self._save_csv_to_message(message)

        return message

    def _save_csv_to_message(self, message: "ChatMessageModel") -> None:
        """Copy the CSV file into the conversation folder and update message filename."""
        folder_path = message.conversation.get_conversation_folder_path()
        os.makedirs(folder_path, exist_ok=True)

        filename = f"csv_export_{message.id}.csv"
        dest_path = os.path.join(folder_path, filename)

        shutil.copy2(self.file_path, dest_path)

        message.filename = filename

    def to_front_dto(self) -> ChatMessageBase:
        return ChatMessageCsvExportFront(
            id=self.id,
            file_name=self.file_name,
            row_count=self.row_count,
        )


class ChatMessageCsvExportFront(ChatMessageBase):
    """Front-end DTO for CSV export messages, without the file_path for security."""

    message_type: str = "csv-export"
    role: str = "assistant"
    file_name: str
    row_count: int
