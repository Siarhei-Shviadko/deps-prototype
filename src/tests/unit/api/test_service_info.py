from deps_prototype.api.constants import BASE_API_PREFIX


class TestServiceInfo:
    endpoint = BASE_API_PREFIX + "/service-info"

    def test_version(self, client):
        response = client.get(f"{self.endpoint}/version")

        assert response.status_code == 200
