import uuid


class FakeUsers:
    def __init__(self, client: "FakeNotionClient") -> None:
        self.client = client

    def me(self) -> dict[str, object]:
        self.client.calls.append(("users.me", {}))
        return {"id": self.client.user_id, "name": self.client.user_name, "type": "bot"}


class FakePages:
    def __init__(self, client: "FakeNotionClient") -> None:
        self.client = client

    def create(self, **kwargs: object) -> dict[str, object]:
        self.client.calls.append(("pages.create", kwargs))
        return {"id": "page-1", "object": "page", **kwargs}

    def retrieve(self, **kwargs: object) -> dict[str, object]:
        self.client.calls.append(("pages.retrieve", kwargs))
        return {"id": kwargs.get("page_id"), "object": "page"}

    def update(self, **kwargs: object) -> dict[str, object]:
        self.client.calls.append(("pages.update", kwargs))
        return {"id": kwargs.get("page_id"), "object": "page", **kwargs}


class FakeNotionClient:
    def __init__(self, user_id: str | None = None, user_name: str = "Test User") -> None:
        self.user_id = user_id or str(uuid.uuid4())
        self.user_name = user_name
        self.calls: list[tuple[str, dict[str, object]]] = []
        self.users = FakeUsers(self)
        self.pages = FakePages(self)

    def search(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("search", kwargs))
        return {
            "object": "list",
            "results": [{"id": "page-1", "object": "page"}],
            **kwargs,
        }
