"""P0: integridade do quiz e semântica due vs session."""

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

    def _seed_and_session(self, headers: dict, limit: int = 3) -> dict:
        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        session = self.client.post(
            "/v1/study-sessions",
            json={"limit": limit},
            headers=headers,
        )
        self.assertEqual(session.status_code, 200, session.text)
        return session.json()

    def test_due_has_no_side_effect_and_no_questions(self) -> None:
        auth = self._register("due-ro@example.com")
        headers = self._headers(auth["access_token"])
        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        due = self.client.get("/v1/reviews/due", headers=headers)
        self.assertEqual(due.status_code, 200)
        body = due.json()
        self.assertIn("words", body)
        self.assertNotIn("questions", body)

    def test_session_never_includes_correct(self) -> None:
        auth = self._register("no-correct@example.com")
        body = self._seed_and_session(self._headers(auth["access_token"]))
        for q in body["questions"]:
            self.assertIn("question_id", q)
            self.assertNotIn("correct", q)

    def test_double_session_reuses_question_ids(self) -> None:
        auth = self._register("nofarm@example.com")
        headers = self._headers(auth["access_token"])
        first = self._seed_and_session(headers)
        second = self.client.post(
            "/v1/study-sessions",
            json={"limit": 3},
            headers=headers,
        ).json()
        ids1 = {q["question_id"] for q in first["questions"]}
        ids2 = {q["question_id"] for q in second["questions"]}
        self.assertEqual(ids1, ids2)

    def test_cannot_forge_question_id(self) -> None:
        auth = self._register("forge@example.com")
        headers = self._headers(auth["access_token"])
        forged = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": "q_forged_not_real_12345678",
                "selected": "luz",
                "idempotency_key": "forge-1",
            },
            headers=headers,
        )
        self.assertEqual(forged.status_code, 422)

    def test_idempotency_conflict_different_question(self) -> None:
        auth = self._register("idemp-conflict@example.com")
        headers = self._headers(auth["access_token"])
        session = self._seed_and_session(headers, limit=2)
        qs = session["questions"]
        if len(qs) < 2:
            self.skipTest("precisa de 2 perguntas")

        key = "one-key"
        self.assertEqual(
            self.client.post(
                "/v1/reviews/answer",
                json={
                    "question_id": qs[0]["question_id"],
                    "selected": qs[0]["options"][0],
                    "idempotency_key": key,
                },
                headers=headers,
            ).status_code,
            200,
        )
        conflict = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": qs[1]["question_id"],
                "selected": qs[1]["options"][0],
                "idempotency_key": key,
            },
            headers=headers,
        )
        self.assertEqual(conflict.status_code, 409)

    def test_user_cannot_answer_another_users_question(self) -> None:
        alice = self._register("alice-q2@example.com")
        bob = self._register("bob-q2@example.com")
        session = self._seed_and_session(self._headers(alice["access_token"]), 1)
        q = session["questions"][0]
        stolen = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": q["options"][0],
                "idempotency_key": "bob-steal",
            },
            headers=self._headers(bob["access_token"]),
        )
        self.assertEqual(stolen.status_code, 422)

    def test_manifest_protects_direct_access(self) -> None:
        self.assertEqual(
            self.client.get("/v1/chapters/dictionary_psalms23/1").status_code, 404
        )
        from api.repositories.content_repo import ContentRepository

        books = ContentRepository().list_available_books()
        self.assertNotIn("dictionary_psalms23", books)

    def test_idempotency_conflict_different_selected(self) -> None:
        auth = self._register("sel-conflict@example.com")
        headers = self._headers(auth["access_token"])
        session = self._seed_and_session(headers, limit=1)
        q = session["questions"][0]
        if len(q["options"]) < 2:
            self.skipTest("precisa de 2 opções")
        key = "same-qid-diff-selected"
        first = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": q["options"][0],
                "idempotency_key": key,
            },
            headers=headers,
        )
        self.assertEqual(first.status_code, 200, first.text)
        conflict = self.client.post(
            "/v1/reviews/answer",
            json={
                "question_id": q["question_id"],
                "selected": q["options"][1],
                "idempotency_key": key,
            },
            headers=headers,
        )
        self.assertEqual(conflict.status_code, 409, conflict.text)

    def test_session_does_not_reuse_across_native_lang(self) -> None:
        auth = self._register("lang-reuse@example.com")
        headers = self._headers(auth["access_token"])
        self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        pt = self.client.post(
            "/v1/study-sessions",
            json={"limit": 1, "native_lang": "pt"},
            headers=headers,
        ).json()
        es = self.client.post(
            "/v1/study-sessions",
            json={"limit": 1, "native_lang": "es"},
            headers=headers,
        ).json()
        if not pt["questions"] or not es["questions"]:
            self.skipTest("sem perguntas para pt/es")
        self.assertNotEqual(
            pt["questions"][0]["question_id"],
            es["questions"][0]["question_id"],
        )


if __name__ == "__main__":
    unittest.main()
