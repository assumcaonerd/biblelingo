import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "biblelingo.db"
        self.previous_db_path = os.environ.get("BIBLELINGO_DB_PATH")
        os.environ["BIBLELINGO_DB_PATH"] = str(self.db_path)
        self.client = TestClient(app)

    def tearDown(self):
        if self.previous_db_path is None:
            os.environ.pop("BIBLELINGO_DB_PATH", None)
        else:
            os.environ["BIBLELINGO_DB_PATH"] = self.previous_db_path
        self.temp_dir.cleanup()

    def test_health_and_progress_are_available(self):
        health = self.client.get("/health")
        progress = self.client.get("/v1/progress")

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")
        self.assertEqual(progress.status_code, 200)
        self.assertEqual(progress.json()["xp"], 0)
        self.assertEqual(progress.json()["level"], 1)

    def test_review_answer_is_atomic_and_idempotent(self):
        payload = {
            "word": "light",
            "selected": "luz",
            "native_lang": "pt",
            "idempotency_key": "session-1-question-1",
        }

        first = self.client.post(
            "/v1/reviews/answer",
            json=payload,
            headers={"X-User-ID": "alice"},
        )
        repeated = self.client.post(
            "/v1/reviews/answer",
            json=payload,
            headers={"X-User-ID": "alice"},
        )

        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(repeated.status_code, 200, repeated.text)
        self.assertTrue(first.json()["is_correct"])
        self.assertFalse(first.json()["already_processed"])
        self.assertTrue(repeated.json()["already_processed"])
        self.assertEqual(first.json()["xp_awarded"], 10)
        self.assertEqual(repeated.json()["xp_awarded"], 10)

        progress = self.client.get(
            "/v1/progress",
            headers={"X-User-ID": "alice"},
        ).json()
        self.assertEqual(progress["xp"], 10)
        self.assertEqual(progress["current_streak"], 1)

    def test_users_are_isolated(self):
        response = self.client.post(
            "/v1/reviews/answer",
            json={
                "word": "light",
                "selected": "luz",
                "native_lang": "pt",
                "idempotency_key": "same-key",
            },
            headers={"X-User-ID": "alice"},
        )
        self.assertEqual(response.status_code, 200)

        bob_progress = self.client.get(
            "/v1/progress",
            headers={"X-User-ID": "bob"},
        ).json()
        self.assertEqual(bob_progress["xp"], 0)
        self.assertEqual(bob_progress["current_streak"], 0)

    def test_server_rejects_unknown_translation(self):
        response = self.client.post(
            "/v1/reviews/answer",
            json={
                "word": "light",
                "selected": "luz",
                "native_lang": "xx",
                "idempotency_key": "invalid-language",
            },
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
