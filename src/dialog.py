class DialogEngine:
    def __init__(self, messages):
        self.messages = messages if isinstance(messages, list) else [messages]
        self.current_index = 0
        self.finished = False

    def get_current_message(self):
        if self.finished or self.current_index >= len(self.messages):
            return None
        return self.messages[self.current_index]

    def next(self):
        self.current_index += 1
        if self.current_index >= len(self.messages):
            self.finished = True

    def is_finished(self):
        return self.finished