__all__ = ["Comparer"]


class Comparer:
    @staticmethod
    def is_content_satisfying(keys: set[str], content: str) -> bool:
        for key in keys:
            if key.lower().strip() == content.lower().strip():
                return True

        return False
