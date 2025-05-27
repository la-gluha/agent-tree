class Context:
    def __init__(self):
        self.history = []

    def add_message(self, role: str, content: str):
        message = {"role": role, "content": content}
        self.history.append(message)

    def get_history(self) -> list:
        return self.history
