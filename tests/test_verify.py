import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx

from lib import verify


def response(status=200, payload=None, text=None, extensions=None):
    request = httpx.Request("GET", "https://unit.test/resource")
    if payload is not None:
        return httpx.Response(status, json=payload, request=request, extensions=extensions or {})
    return httpx.Response(status, text=text or "", request=request, extensions=extensions or {})


def request_double(reply=None, error=None):
    get = AsyncMock(return_value=reply)
    if error is not None:
        get.side_effect = error
    return SimpleNamespace(get=get)


class VerifyTests(unittest.IsolatedAsyncioTestCase):
    async def test_check_update_detects_newer_remote_version(self):
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request", return_value=request_double(response(payload={"version": "0.0.4"}))):
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result, {
            "status": "update_available",
            "local_version": "0.0.3",
            "remote_version": "0.0.4",
        })

    async def test_check_update_reports_matching_version(self):
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request", return_value=request_double(response(payload={"version": "0.0.3"}))):
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result["status"], "up_to_date")

    async def test_check_update_treats_synthetic_transport_599_as_unknown(self):
        synthetic = response(599, text="transport failure", extensions={"phunter_error": "ConnectTimeout"})
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request", return_value=request_double(synthetic)):
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result["status"], "unknown")
        self.assertIsNone(result["remote_version"])

    async def test_check_update_catches_raised_timeout(self):
        timeout = httpx.ReadTimeout("simulated timeout")
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request", return_value=request_double(error=timeout)):
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result["status"], "unknown")

    async def test_check_update_does_not_parse_non_200_response(self):
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request", return_value=request_double(response(503, payload={"version": "9.9.9"}))):
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result["status"], "unknown")
        self.assertIsNone(result["remote_version"])

    async def test_check_update_rejects_invalid_json(self):
        with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
             patch.object(verify, "Request", return_value=request_double(response(text="not json"))):
            result = await verify.check_update("https://unit.test/config.json")
        self.assertEqual(result["status"], "unknown")

    async def test_check_update_rejects_missing_or_malformed_version(self):
        for payload in ({}, {"version": 4}, ["0.0.4"]):
            with self.subTest(payload=payload):
                with patch.object(verify, "_read_local_version", return_value="0.0.3"), \
                     patch.object(verify, "Request", return_value=request_double(response(payload=payload))):
                    result = await verify.check_update("https://unit.test/config.json")
                self.assertEqual(result["status"], "unknown")

    async def test_test_url_first_non_200_does_not_reference_unbound_name(self):
        replies = [response(403), response(200)]
        with patch.object(verify, "Request") as request_cls:
            request_cls.side_effect = [request_double(item) for item in replies]
            results = await verify.test_url([
                ("blocked-first", "https://unit.test/blocked"),
                ("working-second", "https://unit.test/working"),
            ])

        self.assertEqual(results[0]["name"], "blocked-first")
        self.assertEqual(results[0]["reachability"], "reachable")
        self.assertEqual(results[0]["http_result"], "client_error")
        self.assertEqual(results[1]["name"], "working-second")

    async def test_test_url_classifies_http_replies_and_does_not_claim_feature_success(self):
        replies = [response(200), response(302), response(403), response(503)]
        services = [(f"service-{index}", f"https://unit.test/{index}") for index in range(len(replies))]
        with patch.object(verify, "Request") as request_cls:
            request_cls.side_effect = [request_double(item) for item in replies]
            results = await verify.test_url(services)

        self.assertEqual([item["reachability"] for item in results], ["reachable"] * 4)
        self.assertEqual([item["http_result"] for item in results], [
            "success", "redirect", "client_error", "server_error",
        ])
        self.assertEqual({item["functionality"] for item in results}, {"not_checked"})

    async def test_test_url_does_not_assume_unmarked_599_is_a_transport_failure(self):
        # Without Request's marker this is treated as a real HTTP reply.
        with patch.object(verify, "Request", return_value=request_double(response(599))):
            results = await verify.test_url([("http-599", "https://unit.test/599")])
        self.assertEqual(results[0]["reachability"], "reachable")
        self.assertEqual(results[0]["http_result"], "server_error")

    async def test_test_url_marks_synthetic_timeout_as_unreachable(self):
        synthetic = response(599, text="synthetic", extensions={"phunter_error": "ReadTimeout"})
        with patch.object(verify, "Request", return_value=request_double(synthetic)):
            results = await verify.test_url([("timeout-service", "https://unit.test/timeout")])
        self.assertEqual(results[0]["reachability"], "unreachable")
        self.assertEqual(results[0]["http_result"], "transport_error")
        self.assertEqual(results[0]["error"], "ReadTimeout")

    async def test_test_url_handles_raised_timeout_and_no_response(self):
        with patch.object(verify, "Request") as request_cls:
            request_cls.side_effect = [
                request_double(error=TimeoutError()),
                request_double(None),
            ]
            results = await verify.test_url([
                ("raised-timeout", "https://unit.test/timeout"),
                ("empty-response", "https://unit.test/empty"),
            ])

        self.assertEqual(results[0]["reachability"], "unknown")
        self.assertEqual(results[0]["error"], "TimeoutError")
        self.assertEqual(results[1]["http_result"], "no_response")
        self.assertEqual(results[1]["functionality"], "not_checked")


if __name__ == "__main__":
    unittest.main()
