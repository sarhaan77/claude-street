import httpx

from claude_street.auth import get_valid_token

TRADER_BASE = "https://api.schwabapi.com/trader/v1"
MARKET_BASE = "https://api.schwabapi.com/marketdata/v1"


class SchwabClient:
    def __init__(self) -> None:
        self._client = httpx.Client(timeout=30)

    def _headers(self) -> dict:
        token = get_valid_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        resp = self._client.request(method, url, headers=self._headers(), **kwargs)
        resp.raise_for_status()
        return resp

    def trader_get(self, path: str, **kwargs) -> httpx.Response:
        return self._request("GET", f"{TRADER_BASE}{path}", **kwargs)

    def trader_post(self, path: str, **kwargs) -> httpx.Response:
        return self._request("POST", f"{TRADER_BASE}{path}", **kwargs)

    def trader_put(self, path: str, **kwargs) -> httpx.Response:
        return self._request("PUT", f"{TRADER_BASE}{path}", **kwargs)

    def trader_delete(self, path: str, **kwargs) -> httpx.Response:
        return self._request("DELETE", f"{TRADER_BASE}{path}", **kwargs)

    def market_get(self, path: str, **kwargs) -> httpx.Response:
        return self._request("GET", f"{MARKET_BASE}{path}", **kwargs)


def get_client() -> SchwabClient:
    return SchwabClient()
