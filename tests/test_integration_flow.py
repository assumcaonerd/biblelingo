"""Integração: ler → seed → due (leitura) → session → answer → progresso."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.database import initialize_database
from api.main import app


class FullLearningFlowTests(unittest.TestCase):
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
            json={
                "email": email,
                "password": "secret123",
                "native_language": "pt",
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def test_read_seed_due_session_answer_progress_flow(self) -> None:
        auth = self._register("flow@example.com")
        headers = self._headers(auth["access_token"])

        chapter = self.client.get("/v1/chapters/genesis/1")
        self.assertEqual(chapter.status_code, 200, chapter.text)
        self.assertFalse(chapter.json().get("complete", True))

        progress0 = self.client.get("/v1/progress", headers=headers).json()
        self.assertEqual(progress0["xp"], 0)

        seed = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        self.assertEqual(seed.status_code, 200, seed.text)
        self.assertGreater(seed.json()["words_new"], 0)

        due = self.client.get("/v1/reviews/due?limit=5", headers=headers)
        self.assertEqual(due.status_code, 200)
        self.assertGreaterEqual(due.json()["count"], 1)
        self.assertIn("words", due.json())

        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": 5},
            headers=headers,
        )
        self.assertEqual(session.status_code, 200, session.text)
        questions = session.json()["questions"]
        self.assertTrue(questions)
        first = questions[0]
        self.assertNotIn("correct", first)

        correct = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": first["question_id"],
                "selected": first["options"][0],
                "idempotency_key": f"flow-correct-{first['word']}",
            },
            headers=headers,
        )
        self.assertEqual(correct.status_code, 200, correct.text)
        correct_body = correct.json()
        self.assertFalse(correct_body["already_processed"])

        progress1 = self.client.get("/v1/progress", headers=headers).json()
        self.assertEqual(progress1["xp"], correct_body["xp_awarded"])

        repeated = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": first["question_id"],
                "selected": first["options"][0],
                "idempotency_key": f"flow-correct-{first['word']}",
            },
            headers=headers,
        )
        self.assertTrue(repeated.json()["already_processed"])
        self.assertEqual(
            self.client.get("/v1/progress", headers=headers).json()["xp"],
            progress1["xp"],
        )

        seed_again = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        self.assertEqual(seed_again.json()["words_new"], 0)

    def test_two_users_full_flow_remain_isolated(self) -> None:
        alice = self._register("alice-flow@example.com")
        bob = self._register("bob-flow@example.com")
        alice_h = self._headers(alice["access_token"])
        bob_h = self._headers(bob["access_token"])

        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=alice_h,
        )
        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": 1},
            headers=alice_h,
        ).json()
        q = session["questions"][0]

        answer = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": q["options"][0],
                "idempotency_key": "alice-only",
            },
            headers=alice_h,
        )
        self.assertEqual(answer.status_code, 200)
        answer_body = answer.json()

        alice_progress = self.client.get("/v1/progress", headers=alice_h).json()
        bob_progress = self.client.get("/v1/progress", headers=bob_h).json()
        self.assertEqual(alice_progress["xp"], answer_body["xp_awarded"])
        self.assertEqual(bob_progress["xp"], 0)


if __name__ == "__main__":
    unittest.main()
