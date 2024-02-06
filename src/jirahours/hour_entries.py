from datetime import date

from jirahours.hour_entry import HourEntry


class HourEntries:

    def __init__(self) -> None:
        self.entries: list[HourEntry] = []

    @property
    def valid_entries(self) -> list[HourEntry]:
        return [e for e in self.entries if not e.skip()]

    def add_entry(self, entry: HourEntry) -> None:
        self.entries.append(entry)

    def min_date(self) -> date:
        dates = [e.date for e in self.valid_entries]
        return min(dates)

    def max_date(self) -> date:
        dates = [e.date for e in self.valid_entries]
        return max(dates)

    def hours_per_date(self, d: date) -> float:
        seconds = sum([e.seconds for e in self.valid_entries if e.date == d])
        return seconds / 60 / 60

    def tickets(self) -> list[str]:
        t = list(set([e.ticket for e in self.valid_entries]))
        t.sort()
        return t

    def hours_per_ticket(self, ticket: str) -> float:
        seconds = sum([e.seconds for e in self.valid_entries if e.ticket == ticket])
        return seconds / 60 / 60
