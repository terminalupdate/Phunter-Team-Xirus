import unittest
from unittest.mock import AsyncMock

import httpx

from lib.Requests import Request


class RequestTests(unittest.IsolatedAsyncioTestCase):
    async def test_httpx_timeout_becomes_marked_synthetic_599(self):
        client = type("FakeClient", (), {})()
        client.get = AsyncMock(side_effect=httpx.ConnectTimeout("simulated connect timeout"))

        result = await Request("https://unit.test/", client=client).get()

        self.assertEqual(result.status_code, 599)
        self.assertEqual(result.extensions.get("phunter_error"), "ConnectTimeout")
        self.assertIn("no http response", result.text.lower())

    async def test_real_http_response_is_returned_unchanged(self):
        expected = httpx.Response(
            503,
            text="simulated service unavailable",
            request=httpx.Request("GET", "https://unit.test/"),
        )
        client = type("FakeClient", (), {})()
        client.get = AsyncMock(return_value=expected)

        result = await Request("https://unit.test/", client=client).get()

        self.assertIs(result, expected)
        self.assertEqual(result.status_code, 503)
        self.assertNotIn("phunter_error", result.extensions)


if __name__ == "__main__":
    unittest.main()
