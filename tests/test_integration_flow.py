"""Integração do fluxo completo: ler → seed → due → answer → progresso."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.database import initialize_database
from api.main import app


class FullLearningFlowTests(unittest.TestCase):
    """Garante o ciclo pedagógico ponta a ponta sem regressão."""

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

    def test_read_seed_due_answer_progress_flow(self) -> None:
        # 1. Conta
        auth = self._register("flow@example.com")
        headers = self._headers(auth["access_token"])

        # 2. Leitura pública do capítulo
        chapter = self.client.get("/v1/chapters/genesis/1")
        self.assertEqual(chapter.status_code, 200, chapter.text)
        chapter_body = chapter.json()
        self.assertEqual(chapter_body["book"], "genesis")
        self.assertEqual(chapter_body["chapter"], 1)
        self.assertGreater(len(chapter_body["verses"]), 0)

        # 3. Progresso inicial
        progress0 = self.client.get("/v1/progress", headers=headers).json()
        self.assertEqual(progress0["xp"], 0)
        self.assertEqual(progress0["level"], 1)
        self.assertEqual(progress0["current_streak"], 0)

        # 4. Seed do capítulo (CTA do leitor)
        seed = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        self.assertEqual(seed.status_code, 200, seed.text)
        seed_body = seed.json()
        self.assertGreater(seed_body["words_new"], 0)
        self.assertGreater(seed_body["due_count"], 0)

        # 5. Fila de revisão a partir do vocabulário do capítulo
        due = self.client.get("/v1/reviews/due?limit=5", headers=headers)
        self.assertEqual(due.status_code, 200, due.text)
        due_body = due.json()
        self.assertGreaterEqual(due_body["count"], 1)
        questions = due_body["questions"]
        self.assertTrue(questions)

        first = questions[0]
        self.assertIn(first["correct"], first["options"])

        # 6. Resposta correta
        correct_payload = {
            "word": first["word"],
            "selected": first["correct"],
            "native_lang": "pt",
            "idempotency_key": f"flow-correct-{first['word']}",
        }
        correct = self.client.post(
            "/v1/reviews/answer",
            json=correct_payload,
            headers=headers,
        )
        self.assertEqual(correct.status_code, 200, correct.text)
        correct_body = correct.json()
        self.assertTrue(correct_body["is_correct"])
        self.assertFalse(correct_body["already_processed"])
        self.assertGreaterEqual(correct_body["xp_awarded"], 10)

        progress1 = self.client.get("/v1/progress", headers=headers).json()
        self.assertEqual(progress1["xp"], correct_body["xp_awarded"])
        self.assertEqual(progress1["current_streak"], 1)

        # 7. Idempotência da mesma resposta
        repeated = self.client.post(
            "/v1/reviews/answer",
            json=correct_payload,
            headers=headers,
        )
        self.assertEqual(repeated.status_code, 200)
        self.assertTrue(repeated.json()["already_processed"])
        progress_repeat = self.client.get("/v1/progress", headers=headers).json()
        self.assertEqual(progress_repeat["xp"], progress1["xp"])

        # 8. Resposta incorreta em outra palavra (se houver)
        second = next((q for q in questions[1:] if q["word"] != first["word"]), None)
        if second is not None:
            wrong_option = next(
                (opt for opt in second["options"] if opt != second["correct"]),
                None,
            )
            if wrong_option is not None:
                wrong = self.client.post(
                    "/v1/reviews/answer",
                    json={
                        "word": second["word"],
                        "selected": wrong_option,
                        "native_lang": "pt",
                        "idempotency_key": f"flow-wrong-{second['word']}",
                    },
                    headers=headers,
                )
                self.assertEqual(wrong.status_code, 200, wrong.text)
                wrong_body = wrong.json()
                self.assertFalse(wrong_body["is_correct"])
                self.assertEqual(wrong_body["xp_awarded"], 0)
                # XP não sobe no erro
                progress2 = self.client.get("/v1/progress", headers=headers).json()
                self.assertEqual(progress2["xp"], progress1["xp"])

        # 9. Re-seed do mesmo capítulo não duplica
        seed_again = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=headers,
        )
        self.assertEqual(seed_again.status_code, 200)
        self.assertEqual(seed_again.json()["words_new"], 0)
        self.assertEqual(
            seed_again.json()["words_existing"],
            seed_body["words_seen"],
        )

    def test_two_users_full_flow_remain_isolated(self) -> None:
        alice = self._register("alice-flow@example.com")
        bob = self._register("bob-flow@example.com")
        alice_h = self._headers(alice["access_token"])
        bob_h = self._headers(bob["access_token"])

        seed_alice = self.client.post(
            "/v1/vocabulary/seed",
            json={"book": "genesis", "chapter": 1},
            headers=alice_h,
        )
        self.assertEqual(seed_alice.status_code, 200)

        due_alice = self.client.get("/v1/reviews/due?limit=1", headers=alice_h)
        self.assertEqual(due_alice.status_code, 200)
        question = due_alice.json()["questions"][0]

        answer = self.client.post(
            "/v1/reviews/answer",
            json={
                "word": question["word"],
                "selected": question["correct"],
                "native_lang": "pt",
                "idempotency_key": "alice-only",
            },
            headers=alice_h,
        )
        self.assertEqual(answer.status_code, 200)
        self.assertTrue(answer.json()["is_correct"])

        alice_progress = self.client.get("/v1/progress", headers=alice_h).json()
        bob_progress = self.client.get("/v1/progress", headers=bob_h).json()

        self.assertGreater(alice_progress["xp"], 0)
        self.assertEqual(bob_progress["xp"], 0)
        self.assertEqual(bob_progress["current_streak"], 0)


if __name__ == "__main__":
    unittest.main()
