from nilo.cli import core_services as cli_services
from nilo.core.services import provider
from nilo.mcp_server.tools import shared as mcp_services


class FakeClient:
    pass


def test_provider_constructs_services_with_an_injected_client() -> None:
    client = FakeClient()

    assert provider.get_pages_service(client).client is client
    assert provider.get_blocks_service(client).client is client
    assert provider.get_database_compatibility_service(client).client is client


def test_cli_and_mcp_adapters_reexport_core_service_constructors() -> None:
    assert cli_services.get_pages_service is provider.get_pages_service
    assert cli_services.get_databases_service is provider.get_databases_service
    assert mcp_services.get_pages_service is provider.get_pages_service
    assert mcp_services.get_databases_service is provider.get_databases_service
