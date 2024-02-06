from click import ClickException


class CsvError(ClickException):
    def __init__(self, line: int, msg: str):
        # Call the base class constructor with the parameters it needs
        super().__init__(f"csv line {line}: " + msg)
