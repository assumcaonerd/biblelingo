# Contratos TypeScript ↔ Pydantic

`api.ts` espelha os schemas em `api/schemas/` do backend.

| TypeScript | Pydantic |
| --- | --- |
| `User` | `UserOut` |
| `TokenResponse` | `TokenResponse` |
| `Progress` / `LevelProgress` | `ProgressResponse` / `LevelProgress` |
| `Dashboard` / `VocabularyStats` | `DashboardResponse` / `VocabularyStats` |
| `Chapter` / `Verse` | `ChapterOut` / `VerseOut` |
| `ReviewAnswerRequest` | `ReviewAnswerRequest` |
| `ReviewAnswerResponse` | `ReviewAnswerResponse` |
| `DueQuestion` / `DueReviews` | `DueQuestion` / `DueReviewsResponse` |
| `SeedChapterResponse` | `SeedChapterResponse` |

Datas JSON → `string` (ISO). Campos em **snake_case**, iguais ao payload da API.

Quando um schema Pydantic mudar, atualize este arquivo na mesma PR.

Futuro: gerar a partir de `/openapi.json` (openapi-typescript) se a superfície da API crescer muito.
