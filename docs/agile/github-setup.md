# GitHub Kanban / Issues — manual setup

GitHub Projects/Issues cannot be created from this sandbox, so do this once:

1. Push repo to https://github.com/Tanishqnarayan/ScholarSeek
2. Create Project (Board): `ScholarSeek Kanban` with columns:
   BACKLOG, TODO, IN PROGRESS, CODE REVIEW, TESTING, DONE.
3. Create labels: `feature`, `bug`, `testing`, `documentation`,
   `sprint-1`, `sprint-2`, `sprint-3`, `sprint-4`,
   `priority-critical`, `priority-high`, `priority-medium`, `priority-low`.
4. Import 12 issues (title → body → labels):
   - `US-01 Add documents` → "Upload .txt via /manage/, validate, index" → `feature,sprint-1,sprint-3,priority-critical`
   - `US-02 Preprocess` → "lowercase/punct/tokenize/stopwords" → `feature,sprint-1,priority-critical`
   - `US-03 Inverted index` → "dict/set index + JSON save/load" → `feature,sprint-1,priority-critical`
   - `US-04 Search` → "single/multi-term queries" → `feature,sprint-2,priority-critical`
   - `US-05 TF-IDF ranking` → "manual TF-IDF + 0-100%" → `feature,sprint-2,priority-critical`
   - `US-06 Snippets` → "window snippet + highlight" → `feature,sprint-2,priority-high`
   - `US-07 Phrase search` → "`\"...\"` exact phrases" → `feature,sprint-2,sprint-3,priority-high`
   - `US-08 Boolean search` → "AND/OR/NOT + pagination" → `feature,sprint-3,priority-high`
   - `US-09 History` → "SearchQuery/SearchResult pages" → `feature,sprint-3,priority-medium`
   - `US-10 Tests` → "39 unit + 9 Django tests" → `testing,sprint-2,sprint-4,priority-high`
   - `US-11 CI` → ".github/workflows/python-tests.yml" → `documentation,sprint-4,priority-medium`
   - `US-12 Web UI` → "home/results/doc/history/manage" → `feature,sprint-3,priority-high`
   Example: `gh issue create --title "US-01 Add documents" --body "..." --label "feature,sprint-1,priority-critical"`
5. Move all cards to DONE (work in this repo is complete) or to TODO for class demo replay.
