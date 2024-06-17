

class Residue:

    RESIDUE_NAME_PATTERNS = ["residue"]

    @classmethod
    def is_residue(cls, name: str = None):
        """
        Returns True if the compound is a residue, False otherwise
        """

        for pattern in cls.RESIDUE_NAME_PATTERNS:
            if pattern in name:
                return True

        return False
