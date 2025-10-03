from collections import deque


class FairQueue:
    def __init__(self) -> None:
        self.queue = deque()
        self.data = {}

    def add(self, user, msg) -> None:
        if user not in self.data:
            self.queue.append(user)
        self.data[user] = msg

    def current(self) -> tuple():
        if not self.queue:
            return None
        return self.queue[0], self.data[self.queue[0]]

    def next_turn(self) -> tuple():
        if not self.queue:
            return None
        user = self.queue.popleft()
        msg = self.data[user]
        self.queue.append(user)
        return user, msg

    def is_turn(self, user) -> bool:
        return self.queue and self.queue[0] == user

    def users(self):
        return list(self.queue)
