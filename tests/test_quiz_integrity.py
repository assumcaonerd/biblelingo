"""P0: integridade do quiz — sem correct no due, answer só com question_id."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.database import initialize_database
from api.main import app


class QuizIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "biblelingo.db"
        self.previous_db_path = os.environ.get("BIBLELINGO_DB_PATH")
        os.environ["BIBLELINGO_DB_PATH"] = str(self.db_path)
        os.environ.setdefault("BIBLELINGO_ENV", "test")
        os.environ.setdefault(
            "BIBLELINGO_SECRET_KEY", "ci-test-secret-not-for-production"
        )
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

    def test_due_does_not_include_correct(self) -> None:
        auth = self._register("integrity-due@example.com")
        headers = self._headers(auth["access_token"])

        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        due = self.client.get("/v1/reviews/due?limit=3", headers=headers)
        self.assertEqual(due.status_code, 200, due.text)
        body = due.json()
        self.assertGreater(body["count"], 0)
        for q in body["questions"]:
            self.assertIn("question_id", q)
            self.assertNotIn("correct", q)
            self.assertIn("options", q)
            self.assertGreaterEqual(len(q["options"]), 2)

    def test_due_without_vocabulary_is_empty_no_seed(self) -> None:
        auth = self._register("integrity-empty@example.com")
        headers = self._headers(auth["access_token"])
        due = self.client.get("/v1/reviews/due", headers=headers)
        self.assertEqual(due.status_code, 200)
        self.assertEqual(due.json()["count"], 0)

    def test_answer_requires_question_id(self) -> None:
        auth = self._register("integrity-qid@example.com")
        headers = self._headers(auth["access_token"])
        bad = self.client.post(
            "/v1/reviews/answer",
            json={
                "word": "light",
                "selected": "luz",
                "native_lang": "pt",
                "idempotency_key": "x",
            },
            headers=headers,
        )
        self.assertEqual(bad.status_code, 422)

    def test_cannot_answer_without_issued_question(self) -> None:
        auth = self._register("integrity-forge@example.com")
        headers = self._headers(auth["access_token"])
        forged = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": "q_forged_not_real_123456",
                "selected": "luz",
                "idempotency_key": "forge-1",
            },
            headers=headers,
        )
        self.assertEqual(forged.status_code, 422)
        self.assertIn("Unknown question_id", forged.json()["detail"])

    def test_answer_flow_with_question_id(self) -> None:
        auth = self._register("integrity-flow@example.com")
        headers = self._headers(auth["access_token"])

        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        due = self.client.get("/v1/reviews/due?limit=1", headers=headers).json()
        q = due["questions"][0]
        # Cliente não conhece correct; escolhe primeira opção e confere estrutura
        selected = q["options"][0]
        answer = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": selected,
                "idempotency_key": "flow-1",
            },
            headers=headers,
        )
        self.assertEqual(answer.status_code, 200, answer.text)
        body = answer.json()
        self.assertEqual(body["question_id"], q["question_id"])
        self.assertIn("correct_answer", body)
        self.assertIn("is_correct", body)

        # Replay com mesma key
        again = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": selected,
                "idempotency_key": "flow-1",
            },
            headers=headers,
        )
        self.assertEqual(again.status_code, 200)
        self.assertTrue(again.json()["already_processed"])

        # Mesma pergunta, nova key → rejeitada (já respondida)
        second = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": selected,
                "idempotency_key": "flow-2",
            },
            headers=headers,
        )
        self.assertEqual(second.status_code, 422)

    def test_user_cannot_answer_another_users_question(self) -> None:
        alice = self._register("alice-q@example.com")
        bob = self._register("bob-q@example.com")

        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=self._headers(alice["access_token"]),
        )
        due = self.client.get(
            "/v1/reviews/due?limit=1",
            headers=self._headers(alice["access_token"]),
        ).json()
        qid = due["questions"][0]["question_id"]
        option = due["questions"][0]["options"][0]

        stolen = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": qid,
                "selected": option,
                "idempotency_key": "bob-steal",
            },
            headers=self._headers(bob["access_token"]),
        )
        self.assertEqual(stolen.status_code, 422)

    def test_content_manifest_excludes_dictionaries(self) -> None:
        from api.repositories.content_repo import ContentRepository

        books = ContentRepository().list_available_books()
        self.assertIn("genesis", books)
        self.assertIn("psalms", books)
        self.assertNotIn("dictionary_psalms23", books)
        self.assertNotIn("dictionary", books)

        chapter = ContentRepository().get_chapter("genesis", 1)
        self.assertFalse(chapter["complete"])
        self.assertIn("amostra", (chapter.get("label") or "").lower())


if __name__ == "__main__":
    unittest.main()
