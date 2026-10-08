# ScholarSeek — Agile Artifacts

## User Stories (with story points + priority)

| ID | Story | Points | Priority |
|----|-------|--------|----------|
| US-01 | As a user, I want to add academic documents so that they become searchable. | 5 | Critical |
| US-02 | As the system, I want to preprocess documents so that text can be indexed consistently. | 3 | Critical |
| US-03 | As the system, I want to build an inverted index so that documents can be retrieved efficiently. | 5 | Critical |
| US-04 | As a user, I want to search academic documents so that I can find relevant information. | 5 | Critical |
| US-05 | As a user, I want search results ranked by relevance so that the best results appear first. | 8 | Critical |
| US-06 | As a user, I want to see relevant snippets so that I can understand why a result matched. | 3 | High |
| US-07 | As a user, I want phrase search so that I can search exact expressions. | 3 | High |
| US-08 | As a user, I want Boolean search so that I can make advanced queries. | 5 | High |
| US-09 | As a user, I want my search history saved so that I can review previous searches. | 3 | Medium |
| US-10 | As a developer, I want automated tests so that changes do not break existing functionality. | 5 | High |
| US-11 | As a developer, I want CI checks to run automatically when code is pushed. | 3 | Medium |
| US-12 | As a user, I want a clean web interface so that searching is easy. | 5 | High |

Total: 53 points.

## Product Backlog (priority order)

1. US-03 inverted index (5, Critical) — DONE (Sprint 1)
2. US-02 preprocessing (3, Critical) — DONE (Sprint 1)
3. US-01 document loader + upload (5, Critical) — DONE (Sprint 1 + 3)
4. US-04 search (5, Critical) — DONE (Sprint 2)
5. US-05 TF-IDF ranking (8, Critical) — DONE (Sprint 2)
6. US-06 snippets (3, High) — DONE (Sprint 2)
7. US-07 phrase search (3, High) — DONE (Sprint 2/3)
8. US-08 boolean search (5, High) — DONE (Sprint 3)
9. US-12 web UI (5, High) — DONE (Sprint 3)
10. US-10 tests (5, High) — DONE (Sprint 2/4)
11. US-09 history (3, Medium) — DONE (Sprint 3)
12. US-11 CI (3, Medium) — DONE (Sprint 4)

## Sprint Backlogs

### Sprint 1 — Core document processing and indexing (13 pts, 1 week)
Goal: load + normalize + index documents.
- Project setup (2) — DONE
- Document loader + validation + metadata (3, US-01 part) — DONE
- Preprocessor + tokenizer + stopwords (3, US-02) — DONE
- Inverted index + JSON save/load (5, US-03) — DONE

### Sprint 2 — Search and ranking (19 pts)
Goal: query → ranked snippets.
- Query processing (3, US-04) — DONE
- TF scoring + TF-IDF ranking + sorting (8, US-05) — DONE
- Snippet generation (3, US-06) — DONE
- Phrase matching (3, US-07 part) — DONE
- Unit tests for core (2, US-10 part) — DONE

### Sprint 3 — Django application (16 pts)
Goal: usable web app with history + advanced search.
- Django setup + search UI + results page (5, US-12) — DONE
- Document page + history models/views (3, US-09) — DONE
- Boolean AND/OR/NOT + pagination (5, US-08) — DONE
- Upload + rebuild_index command (3, US-01 rest) — DONE

### Sprint 4 — Testing, CI/CD, finalization (5 pts)
Goal: green CI + docs.
- Integration/Django tests (2, US-10 rest) — DONE
- GitHub Actions workflow (1, US-11) — DONE
- Cleanup + README + Agile docs (2) — DONE

## Kanban Workflow

Columns: BACKLOG → TODO → IN PROGRESS → CODE REVIEW → TESTING → DONE.
All 12 stories are DONE. Labels used: `feature`, `testing`, `documentation`,
`sprint-1..4`, `priority-critical/high/medium/low`.

Manual GitHub setup (Projects cannot be created from this environment):
see `github-setup.md` — create Project board, 6 columns, import issues via `gh`.

## Burndown

- Total: 53 pts; completed: 53; remaining: 0.
- Sprint durations: 1 week each (4 weeks total).
- Source of truth: `burndown.json` / `burndown.csv` (update `done` per day).
- Regenerate chart: `python scripts/burndown.py` → `docs/agile/burndown.svg`
  (stdlib only, no matplotlib/numpy/pandas).

## Definition of Done

See `definition_of_done.md`.
