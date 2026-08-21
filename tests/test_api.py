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
        self.assertGreater(first.json()["words_new"], 0)
        self.assertEqual(second.json()["words_new"], 0)

        due = self.client.get("/v1/reviews/due?limit=5", headers=headers)
        self.assertEqual(due.status_code, 200)
        self.assertGreaterEqual(due.json()["count"], 1)
        self.assertIn("words", due.json())

    def test_psalms23_content_and_seed(self):
        chapter = self.client.get("/v1/chapters/psalms/23")
        self.assertEqual(chapter.status_code, 200, chapter.text)
        body = chapter.json()
        self.assertEqual(body["book"], "psalms")
        self.assertEqual(len(body["verses"]), 6)

        auth = self._register("psalms@example.com")
        headers = self._auth_header(auth["access_token"])
        seeded = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "psalms", "chapter": 23},
            headers=headers,
        )
        self.assertEqual(seeded.status_code, 200, seeded.text)

    def test_due_is_read_only_empty_without_seed(self):
        auth = self._register("due@example.com")
        headers = self._auth_header(auth["access_token"])

        response = self.client.get("/v1/reviews/due?limit=3", headers=headers)
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["count"], 0)
        self.assertEqual(body["words"], [])
        self.assertNotIn("questions", body)

    def test_study_session_emits_questions_without_correct(self):
        auth = self._register("session@example.com")
        headers = self._auth_header(auth["access_token"])
        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )

        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": 3},
            headers=headers,
        )
        self.assertEqual(session.status_code, 200, session.text)
        body = session.json()
        self.assertGreaterEqual(body["count"], 1)
        first = body["questions"][0]
        self.assertIn("question_id", first)
        self.assertNotIn("correct", first)

        # Segunda emissão reutiliza os mesmos question_ids (anti-farming)
        again = self.client.post(
            "/v1/study-sessions",
            json={"limit": 3},
            headers=headers,
        )
        ids1 = {q["question_id"] for q in body["questions"]}
        ids2 = {q["question_id"] for q in again.json()["questions"]}
        self.assertTrue(ids1 & ids2)

    def test_due_requires_auth(self):
        response = self.client.get("/v1/reviews/due")
        self.assertEqual(response.status_code, 401)

    def test_review_answer_via_session_is_idempotent(self):
        auth = self._register("answer@example.com")
        headers = self._auth_header(auth["access_token"])
        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": 1},
            headers=headers,
        ).json()
        q = session["questions"][0]
        selected = q["options"][0]

        payload = {
            "question_id": q["question_id"],
            "selected": selected,
            "idempotency_key": "session-1-question-1",
        }
        first = self.client.post("/v1/reviews/answer", json=payload, headers=headers)
        repeated = self.client.post("/v1/reviews/answer", json=payload, headers=headers)

        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(repeated.status_code, 200, repeated.text)
        self.assertFalse(first.json()["already_processed"])
        self.assertTrue(repeated.json()["already_processed"])

        progress = self.client.get("/v1/progress", headers=headers).json()
        self.assertEqual(progress["xp"], first.json()["xp_awarded"])

    def test_idempotency_key_conflict_on_different_question(self):
        auth = self._register("conflict@example.com")
        headers = self._auth_header(auth["access_token"])
        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": 2},
            headers=headers,
        ).json()
        qs = session["questions"]
        if len(qs) < 2:
            self.skipTest("precisa de ao menos 2 perguntas")

        key = "shared-key"
        first = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": qs[0]["question_id"],
                "selected": qs[0]["options"][0],
                "idempotency_key": key,
            },
            headers=headers,
        )
        self.assertEqual(first.status_code, 200, first.text)

        conflict = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": qs[1]["question_id"],
                "selected": qs[1]["options"][0],
                "idempotency_key": key,
            },
            headers=headers,
        )
        self.assertEqual(conflict.status_code, 409, conflict.text)

    def test_users_are_isolated(self):
        alice = self._register("alice-iso@example.com")
        bob = self._register("bob-iso@example.com")

        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=self._auth_header(alice["access_token"]),
        )
        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": 1},
            headers=self._auth_header(alice["access_token"]),
        ).json()
        q = session["questions"][0]
        self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": q["options"][0],
                "idempotency_key": "alice-key",
            },
            headers=self._auth_header(alice["access_token"]),
        )

        bob_progress = self.client.get(
            "/v1/progress",
            headers=self._auth_header(bob["access_token"]),
        ).json()
        self.assertEqual(bob_progress["xp"], 0)

    def test_unknown_chapter_is_404(self):
        response = self.client.get("/v1/chapters/dictionary_psalms23/1")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
