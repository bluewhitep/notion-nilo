from fastapi.testclient import TestClient

from nilo.server import app, get_notion_client


class FakeDataSources:
    def retrieve(self, data_source_id: str):
        return {"id": data_source_id, "object": "database"}

    def query(self, data_source_id: str, **payload):
        return {"results": [{"id": "row1", "type": "page"}]}


class FakeDatabases:
    def retrieve(self, database_id: str):
        return {"id": database_id, "object": "database"}

    def query(self, database_id: str, **payload):
        return {"results": [], "database_id": database_id, "payload": payload}


class FakeClient:
    def __init__(self):
        self.data_sources = FakeDataSources()
        self.databases = FakeDatabases()

    def search(self, filter):
        # simulate search result
        kind = filter.get("value")
        return {"results": [{"id": f"{kind}-1", "object": kind}]}


class MissingDataSources:
    def retrieve(self, data_source_id: str):
        raise RuntimeError("not a data source")

    def query(self, data_source_id: str, **payload):
        raise RuntimeError("not a data source")


class LegacyDatabaseClient(FakeClient):
    def __init__(self):
        self.data_sources = MissingDataSources()
        self.databases = FakeDatabases()


def override_get_client() -> FakeClient:
    return FakeClient()


def override_get_legacy_database_client() -> LegacyDatabaseClient:
    return LegacyDatabaseClient()


def test_list_databases(monkeypatch):
    app.dependency_overrides[get_notion_client] = override_get_client
    client = TestClient(app)
    resp = client.get("/databases")
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"][0]["object"] == "data_source"


def test_retrieve_database(monkeypatch):
    app.dependency_overrides[get_notion_client] = override_get_client
    client = TestClient(app)
    resp = client.get("/databases/mydb")
    assert resp.status_code == 200
    assert resp.json()["id"] == "mydb"


def test_query_database(monkeypatch):
    app.dependency_overrides[get_notion_client] = override_get_client
    client = TestClient(app)
    resp = client.post("/databases/mydb/query", json={"filter": {"property": "Name"}})
    assert resp.status_code == 200
    assert resp.json()["results"][0]["id"] == "row1"


def test_retrieve_and_query_fall_back_inside_core_service():
    app.dependency_overrides[get_notion_client] = override_get_legacy_database_client
    client = TestClient(app)

    retrieve = client.get("/databases/legacy-db")
    query = client.post("/databases/legacy-db/query", json={"page_size": 1})

    assert retrieve.status_code == 200
    assert retrieve.json()["id"] == "legacy-db"
    assert query.status_code == 200
    assert query.json()["results"] == []


def test_legacy_database_query_path_id_cannot_be_overridden_by_body():
    app.dependency_overrides[get_notion_client] = override_get_legacy_database_client
    client = TestClient(app)

    query = client.post(
        "/databases/path-db/query",
        json={
            "data_source_id": "body-data-source",
            "database_id": "body-db",
            "page_size": 1,
        },
    )

    assert query.status_code == 200
    assert query.json()["database_id"] == "path-db"
    assert "database_id" not in query.json()["payload"]
    assert "data_source_id" not in query.json()["payload"]
