import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.database import initialize_database
from api.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "biblelingo.db"
        self.previous_db_path = os.environ.get("BIBLELINGO_DB_PATH")
        os.environ["BIBLELINGO_DB_PATH"] = str(self.db_path)
        initialize_database()
        self.client = TestClient(app)

    def tearDown(self):
        if self.previous_db_path is None:
            os.environ.pop("BIBLELINGO_DB_PATH", None)
        else:
            os.environ["BIBLELINGO_DB_PATH"] = self.previous_db_path
        self.temp_dir.cleanup()

    def _register(self, email: str, password: str = "secret123", native: str = "pt") -> dict:
        response = self.client.post(
            "/v1/auth/register",
            json={"email": email, "password": password, "native_language": native},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def _auth_header(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def test_health_is_public(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")

    def test_progress_requires_auth(self):
        response = self.client.get("/v1/progress")
        self.assertEqual(response.status_code, 401)

    def test_register_login_and_me(self):
        created = self._register("alice@example.com")
        self.assertIn("access_token", created)
        self.assertEqual(created["user"]["email"], "alice@example.com")

        login = self.client.post(
            "/v1/auth/login",
            json={"email": "alice@example.com", "password": "secret123"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]

        me = self.client.get("/v1/me", headers=self._auth_header(token))
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], "alice@example.com")

    def test_duplicate_email_is_rejected(self):
        self._register("dup@example.com")
        second = self.client.post(
            "/v1/auth/register",
            json={"email": "dup@example.com", "password": "secret123"},
        )
        self.assertEqual(second.status_code, 409)

    def test_seed_chapter_is_idempotent(self):
        auth = self._register("seed@example.com")
        headers = self._auth_header(auth["access_token"])

        first = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        second = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )

        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        body1 = first.json()
        body2 = second.json()
        self.assertGreater(body1["words_seen"], 0)
        self.assertGreater(body1["words_new"], 0)
        self.assertEqual(body2["words_new"], 0)
        self.assertEqual(body1["words_seen"], body2["words_existing"])

        due = self.client.get("/v1/reviews/due?limit=5", headers=headers)
        self.assertEqual(due.status_code, 200)
        self.assertGreaterEqual(due.json()["count"], 1)

    def test_psalms23_content_and_seed(self):
        chapter = self.client.get("/v1/chapters/psalms/23")
        self.assertEqual(chapter.status_code, 200, chapter.text)
        body = chapter.json()
        self.assertEqual(body["book"], "psalms")
        self.assertEqual(body["chapter"], 23)
        self.assertEqual(len(body["verses"]), 6)
        self.assertIn("Yahweh is my shepherd", body["verses"][0]["text"])

        auth = self._register("psalms@example.com")
        headers = self._auth_header(auth["access_token"])
        seeded = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "psalms", "chapter": 23},
            headers=headers,
        )
        self.assertEqual(seeded.status_code, 200, seeded.text)
        self.assertGreater(seeded.json()["words_new"], 0)
        self.assertEqual(
            seeded.json()["words_seen"],
            seeded.json()["words_with_translation"],
        )

    def test_due_reviews_seed_and_return_questions(self):
        auth = self._register("due@example.com")
        headers = self._auth_header(auth["access_token"])

        response = self.client.get("/v1/reviews/due?limit=3", headers=headers)
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertGreaterEqual(body["count"], 1)
        self.assertEqual(body["native_lang"], "pt")
        first = body["questions"][0]
        self.assertIn("word", first)
        self.assertIn("options", first)
        self.assertIn("correct", first)
        self.assertIn(first["correct"], first["options"])

    def test_due_requires_auth(self):
        response = self.client.get("/v1/reviews/due")
        self.assertEqual(response.status_code, 401)

    def test_due_rejects_unsupported_language(self):
        auth = self._register("language@example.com")
        response = self.client.get(
            "/v1/reviews/due?native_lang=xx",
            headers=self._auth_header(auth["access_token"]),
        )
        self.assertEqual(response.status_code, 422)

    def test_review_answer_is_atomic_and_idempotent(self):
        auth = self._register("alice@example.com")
        headers = self._auth_header(auth["access_token"])

        payload = {
            "word": "light",
            "selected": "luz",
            "native_lang": "pt",
            "idempotency_key": "session-1-question-1",
        }

        first = self.client.post("/v1/reviews/answer", json=payload, headers=headers)
        repeated = self.client.post("/v1/reviews/answer", json=payload, headers=headers)

        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(repeated.status_code, 200, repeated.text)
        self.assertTrue(first.json()["is_correct"])
        self.assertFalse(first.json()["already_processed"])
        self.assertTrue(repeated.json()["already_processed"])
        self.assertEqual(first.json()["xp_awarded"], 10)
        self.assertEqual(repeated.json()["xp_awarded"], 10)

        progress = self.client.get("/v1/progress", headers=headers).json()
        self.assertEqual(progress["xp"], 10)
        self.assertEqual(progress["current_streak"], 1)

    def test_users_are_isolated(self):
        alice = self._register("alice@example.com")
        bob = self._register("bob@example.com")

        response = self.client.post(
            "/v1/reviews/answer",
            json={
                "word": "light",
                "selected": "luz",
                "native_lang": "pt",
                "idempotency_key": "same-key",
            },
            headers=self._auth_header(alice["access_token"]),
        )
        self.assertEqual(response.status_code, 200)

        bob_progress = self.client.get(
            "/v1/progress",
            headers=self._auth_header(bob["access_token"]),
        ).json()
        self.assertEqual(bob_progress["xp"], 0)
        self.assertEqual(bob_progress["current_streak"], 0)

    def test_server_rejects_unknown_translation(self):
        auth = self._register("carol@example.com")
        response = self.client.post(
            "/v1/reviews/answer",
            json={
                "word": "light",
                "selected": "luz",
                "native_lang": "xx",
                "idempotency_key": "invalid-language",
            },
            headers=self._auth_header(auth["access_token"]),
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
