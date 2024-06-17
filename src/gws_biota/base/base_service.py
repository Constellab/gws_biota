


class BaseService:
    BATCH_SIZE = 50000

    @staticmethod
    def format_ft_names(text):
        if isinstance(text, str):
            text = text.split()
        if isinstance(text, list):
            text = ";".join(list(set(text)))
        return text
