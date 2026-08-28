import pytest


@pytest.fixture(autouse=True)
def session(containers, mocker):
    database = containers.datasources.postgres_datasource()
    connection = database.engine.connect()

    class _PinnedRegistry:
        pass

    _PinnedRegistry.connection = connection
    original_registry = database._registry
    database._registry = _PinnedRegistry

    outer = connection.begin()
    mocker.patch.object(database, "close_connection")
    try:
        yield
    finally:
        if outer.is_active:
            outer.rollback()
        database._registry = original_registry
        connection.close()
