from requests import Response

from deps_prototype.domain.exceptions import RestClientError
from deps_prototype.extras.rest_client import AbstractRESTClient
from deps_prototype.extras.rest_client.deps_token_auth import DEPSTokenAuth
from deps_prototype.infrastructure.access_management import user

__all__ = ["GenericProxy"]


class GenericProxy(AbstractRESTClient):
    exception: type[RestClientError]

    def _set_authentication(self) -> None:
        self._session.auth = DEPSTokenAuth(user)

    def _check_response(self, response: Response) -> None:
        if not response.ok:
            self._logger.error(
                "Response to %s with payload %s failed with error %s",
                response.url,
                response.request.__dict__,
                response.content,
            )

            raise self.exception(response.content)
