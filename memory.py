class Memory:
    def __init__(self):
        self.entries = []

    def add(self, entry: str):
        self.entries.append(entry)

    def query(self, search_term: str) -> list[str]:
        return [entry for entry in self.entries if search_term in entry]
