"""
Custom Error Classes Used By validator.py
"""


class DateFormatError(Exception):
    """Dates must be YYYY-MM-DD"""

    def __init__(self, message: str):
        super().__init__(f"\n{message}")


class PriorityError(Exception):
    """Priority must be High, Medium, or Low"""

    def __init__(self, message: str):
        super().__init__(f"\n{message}")


if __name__ == "__main__":
    print("'errors.py' is being run directly")
