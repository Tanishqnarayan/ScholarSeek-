# ScholarSeek — Mini Search Engine for Academic Documents

## 1. Project title
ScholarSeek: a mini search engine that indexes local academic `.txt` documents and returns relevance-ranked results. All indexing/scoring/ranking is hand-written in Core Python (stdlib only).

## 2. Problem statement
Students keep notes across many text files (Python, DBMS, OS, ...). `Ctrl+F` finds strings but does not rank, handle phrases/booleans, or explain *why* a file matched. We need a local, explainable search engine.

## 3. Objectives
- Own document loader, preprocessor, inverted index, query parser, TF-IDF ranker, snippet generator.
- Clean Django UI + MySQL history + pagination + advanced syntax.
- 4-sprint Agile delivery with tests + CI.

## 4. Features
- Single/multi-term, case-insensitive search; `"exact phrases"`; `AND`/`OR`/`NOT`; stop-word-safe queries.
- Manual TF-IDF relevance 0–100%, sorted desc; match counts; `<mark>`-highlighted snippets.
- Upload `.txt` (staff), auto re-index, document page, history page, 5-per-page pagination.
- JSON-persisted index (`data/index.json`), `rebuild_index` management command.

## 5. Technology stack
Python 3.13, Django 5/6, MySQL 8 (`mysqlclient`), HTML/CSS + vanilla JS (none required), unittest + Django tests, GitHub Actions. Core engine uses only `re, string, math, json, collections, pathlib, hashlib, difflib(no), logging`.

## 6. System architecture
```
documents/*.txt → loader → preprocessor → indexer (dict/set) → data/index.json
                                                            ↓
browser → Django views → SearchEngine.search() → ranker/snippets → templates
                        ↓ persists SearchQuery/SearchResult → MySQL
```

## 7. Search algorithm explanation
1. Parse query (phrases + boolean groups) with `query_parser.py`.
2. Retrieve candidates from index postings (`AND`=intersect, `OR`=union, `NOT`=subtract; default OR).
3. Score with TF-IDF + coverage + 1.5× phrase boost; normalize best→100%; sort with `lambda r: r.score`.
4. Slice `top_k`, build snippets, paginate.

## 8. Inverted index explanation
`dict[str, set[doc_id]]` e.g. `python → {python.txt, sql.txt}`, plus `doc_term_freqs` and `doc_lengths`. Built in `search_engine/indexer.py`, saved via `to_dict()/save()` to `data/index.json`, reloaded with `load()`.

## 9. Ranking algorithm explanation
Considers query TF (implicit), doc TF (`1+log(freq)`), IDF, matched-term coverage (`0.5+coverage`), phrase boost. See `search_engine/ranker.py`.

## 10. TF-IDF explanation
`tf = 1 + ln(freq)` dampens repetition; `idf = ln((1+N)/(1+df)) + 1` upweights rare terms (e.g. `normalization` > `database`). Product summed per doc, then coverage/phrase adjustments, then `%` normalization.

## 11. Project structure
```
documents/ (8 .txt) | search_engine/ (loader, preprocessor, indexer, query_parser, ranker, snippets, engine)
config/ (settings MySQL/env, urls) | search_app/ (models, views, urls, services, templates, static, rebuild_index)
tests/ (39 unit tests) | data/index.json | scripts/burndown.py | docs/agile/ | .github/workflows/
```

## 12. Installation instructions
```powershell
git clone https://github.com/Tanishqnarayan/ScholarSeek-.git
cd ScholarSeek-  # folder ITL-PBL in this submission
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## 13. MySQL setup
```sql
CREATE DATABASE mini_search_engine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- set DB_PASSWORD if root has one; then in .env:
-- DB_NAME=mini_search_engine DB_USER=root DB_PASSWORD=<pwd> DB_HOST=127.0.0.1 DB_PORT=3306
```
```powershell
python manage.py migrate
python manage.py rebuild_index
python manage.py createsuperuser
```
Tip: `USE_SQLITE=1 python manage.py ...` runs without MySQL for quick evaluation. CI uses a MySQL 8 service (`root/root`).

## 14. Django setup
Settings read `DB_*`, `DJANGO_SECRET_KEY`, `DOCUMENTS_DIR`, `INDEX_PATH` from env (`.env`). `ALLOWED_HOSTS` defaults include localhost/testserver. Static at `search_app/static/`.

## 15. How to run
```powershell
python manage.py rebuild_index
python manage.py runserver
# open http://127.0.0.1:8000 — try: database normalization, "deadlock detection", python AND django
```

## 16. How to add documents
Staff login → `/manage/` → upload `.txt` (≤2 MB, non-empty) → auto re-index + catalog sync. Or drop files into `documents/` and run `python manage.py rebuild_index`.

## 17. How to run tests
```powershell
python -m unittest discover -s tests -v   # 39 core tests
$env:USE_SQLITE="1"; python manage.py test search_app  # 9 Django tests (or with MySQL env)
python scripts/burndown.py
```

## 18. Git workflow
Fresh repo in project dir, remote `origin https://github.com/Tanishqnarayan/ScholarSeek-.git`. Conventional commits: `feat:`, `test:`, `ci:`, `docs:`. Example history: `feat: add document loader`, `feat: implement text preprocessing`, `feat: build inverted index`, `feat: implement search ranking`, `feat: add result snippets`, `feat: add Django search interface`, `test: add indexer tests`, `ci: add GitHub Actions workflow`, `docs: update project documentation`.

## 19. Agile methodology
Scrum, 4×1-week sprints, 12 stories (53 pts). Artifacts in `docs/agile/`: `backlog.md` (stories/points/priorities, product + sprint backlogs, kanban columns, burndown procedure), `definition_of_done.md`, `github-setup.md`, `burndown.json/.csv/.svg`.

## 20. Product backlog
Priority order in `docs/agile/backlog.md`: index → preprocess → loader → search → ranking → snippets → phrase → boolean → UI → tests → history → CI.

## 21. Sprint backlog
Sprint 1 (13): setup/loader/preprocess/index. Sprint 2 (19): query/TF-IDF/snippets/phrase/tests. Sprint 3 (16): UI/history/boolean/upload. Sprint 4 (5): integration tests/CI/docs. All DONE.

## 22. Kanban board
Columns BACKLOG/TODO/IN PROGRESS/CODE REVIEW/TESTING/DONE; labels `feature,bug,testing,documentation,sprint-1..4,priority-*`. Manual import steps in `github-setup.md` (Projects UI + `gh issue create`).

## 23. User story priorities
Critical: US-01..US-05. High: US-06, US-07, US-08, US-10, US-12. Medium: US-09, US-11. Points in `backlog.md` (total 53).

## 24. Burndown chart procedure
Update `burndown.csv` (`completed_today`) as work finishes, keep `burndown.json` totals in sync, run `python scripts/burndown.py` → `burndown.svg` (stdlib SVG, no matplotlib). README totals: 53 pts, 53 done, 0 remaining.

## 25. GitHub Actions CI/CD
`.github/workflows/python-tests.yml` on push/PR: checkout → Python 3.13 → mysqlclient sysdeps → pip install → unit tests → `manage.py check+migrate` → `rebuild_index` → `manage.py test`. Fails closed on any test failure. MySQL 8 service container.

## 26. Future enhancements
PDF support, stemming, positional index, fuzzy (`difflib`) suggestions, per-user history, REST API, Docker Compose.

## 27. Limitations
`.txt` only; English stopword list; no stemming; in-memory index sized for hundreds of docs; snippet highlighter assumes trusted local docs; MySQL required for production history (sqlite fallback is for eval only).
