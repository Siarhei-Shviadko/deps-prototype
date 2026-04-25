import pytest

from deps_prototype.api.constants import BASE_API_PREFIX


class TestDebug:
    endpoint = BASE_API_PREFIX

    def test_debug_endpoint_return_500(self, client):
        with pytest.raises(ValueError):
            client.get(f"{self.endpoint}/debug/500")
