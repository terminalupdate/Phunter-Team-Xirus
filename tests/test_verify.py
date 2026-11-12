import json
import unittest
from unittest.mock import AsyncMock, patch

import httpx

from lib import verify


def response(status=200, payload=None, text=None, extensions=None):
    req = httpx.Request("GET", "https://unit.test/resource")
    if payload is not None:
        return httpx.Response(status, json=payload, request=req, extensions=extensions or {})
    return httpx.Response(status, text=text or "", request=req, extensions=extensions or {})


class VerifyTests(unittest.IsolatedAsyncioTestCase):
    async def test_check_update_uses_response_json_and_compares_versions(self):
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request") as request_cls:
            request_cls.return_value.get = AsyncMock(return_value=response(payload={"version": "0.0.4"}))
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result["status"], "update_available")
        self.assertEqual(result["remote_version"], "0.0.4")

    async def test_check_update_treats_transport_599_as_unknown(self):
        synthetic = response(599, text="transport failure", extensions={"phunter_error": "ConnectTimeout"})
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request") as request_cls:
            request_cls.return_value.get = AsyncMock(return_value=synthetic)
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result["status"], "unknown")

    async def test_check_update_rejects_invalid_json(self):
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request") as request_cls:
            request_cls.return_value.get = AsyncMock(return_value=response(text="not json"))
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result["status"], "unknown")

    async def test_test_url_handles_each_status_without_unbound_name(self):
        replies = [response(200), response(403), response(503),
                   response(599, text="synthetic", extensions={"phunter_error": "ReadTimeout"})]
        with patch.object(verify, "Request") as request_cls:
            request_cls.side_effect = [type("R", (), {"get": AsyncMock(return_value=item)})() for item in replies]
            results = await verify.test_url([(f"service-{i}", f"https://unit.test/{i}") for i in range(4)])
        self.assertEqual([r["reachability"] for r in results],
                         ["reachable", "reachable", "reachable", "unreachable"])
        self.assertEqual([r["http_result"] for r in results],
                         ["success", "client_error", "server_error", "transport_error"])

    async def test_test_url_handles_request_exception(self):
        with patch.object(verify, "Request") as request_cls:
            request_cls.return_value.get = AsyncMock(side_effect=TimeoutError())
            results = await verify.test_url([("timeout-service", "https://unit.test/timeout")])
        self.assertEqual(results[0]["reachability"], "unknown")
        self.assertEqual(results[0]["error"], "TimeoutError")


if __name__ == "__main__":
    unittest.main()
