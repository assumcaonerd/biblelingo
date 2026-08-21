"""Testes do endpoint agregado GET /v1/dashboard."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.database import initialize_database
from api.main import app


class DashboardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "biblelingo.db"
        self.previous_db_path = os.environ.get("BIBLELINGO_DB_PATH")
        os.environ["BIBLELINGO_DB_PATH"] = str(self.db_path)
        initialize_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        if self.previous_db_path is None:
            os.environ.pop("BIBLELINGO_DB_PATH", None)
        else:
            os.environ["BIBLELINGO_DB_PATH"] = self.previous_db_path
        self.temp_dir.cleanup()

    def _register(self, email: str) -> dict:
        response = self.client.post(
            "/v1/auth/register",
            json={"email": email, "password": "secret123", "native_language": "pt"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def test_dashboard_requires_auth(self) -> None:
        response = self.client.get("/v1/dashboard")
        self.assertEqual(response.status_code, 401)

    def test_dashboard_empty_user(self) -> None:
        auth = self._register("empty-dash@example.com")
        response = self.client.get(
            "/v1/dashboard",
            headers=self._headers(auth["access_token"]),
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["progress"]["xp"], 0)
        self.assertEqual(body["vocabulary"]["total_words"], 0)

    def test_dashboard_after_seed_and_review(self) -> None:
        auth = self._register("dash@example.com")
        headers = self._headers(auth["access_token"])

        seed = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        self.assertEqual(seed.status_code, 200)

        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": 1},
            headers=headers,
        )
        self.assertEqual(session.status_code, 200, session.text)
        question = session.json()["questions"][0]

        answer = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": question["question_id"],
                "selected": question["options"][0],
                "idempotency_key": "dash-1",
            },
            headers=headers,
        )
        self.assertEqual(answer.status_code, 200, answer.text)

        dash = self.client.get("/v1/dashboard", headers=headers)
        self.assertEqual(dash.status_code, 200, dash.text)
        body = dash.json()

        self.assertGreater(body["progress"]["xp"], 0)
        self.assertGreater(body["vocabulary"]["total_words"], 0)
        self.assertGreaterEqual(body["reviews_today"], 1)
        self.assertTrue(body["recent_activity"])
        self.assertEqual(body["recent_activity"][0]["word"], question["word"])

    def test_dashboard_isolation(self) -> None:
        alice = self._register("alice-dash@example.com")
        bob = self._register("bob-dash@example.com")

        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=self._headers(alice["access_token"]),
        )
        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": 1},
            headers=self._headers(alice["access_token"]),
        ).json()
        q = session["questions"][0]
        self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": q["options"][0],
                "idempotency_key": "alice-dash",
            },
            headers=self._headers(alice["access_token"]),
        )

        bob_dash = self.client.get(
            "/v1/dashboard",
            headers=self._headers(bob["access_token"]),
        ).json()
        self.assertEqual(bob_dash["progress"]["xp"], 0)
        self.assertEqual(bob_dash["vocabulary"]["total_words"], 0)


if __name__ == "__main__":
    unittest.main()
