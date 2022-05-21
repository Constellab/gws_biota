# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


class BaseService:
    BULK_SIZE = 10000

    @staticmethod
    def format_ft_names(text):
        if isinstance(text, str):
            text = text.split()
        if isinstance(text, list):
            text = ";".join(list(set(text)))
        return text
