# Definition of Done

1. Code implements the linked user story with no `pass`/`TODO` stubs in core paths.
2. PEP 8, clear names, docstrings on public functions, no hardcoded absolute paths.
3. `python -m unittest discover -s tests` passes.
4. `python manage.py check` and `python manage.py test` pass.
5. Manual check: `database normalization` ranks `dbms.txt` first; `"deadlock detection"` finds `os.txt`.
6. Docs updated (README + `docs/agile/burndown.json` if points changed).
7. Committed with a conventional message (`feat:`, `test:`, `ci:`, `docs:`).
