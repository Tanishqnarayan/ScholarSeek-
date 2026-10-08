# One-shot GitHub setup for ScholarSeek: labels + 12 user-story issues + Kanban board.
# Prerequisite (one time, interactive):  gh auth login
# Usage:  .\scripts\setup_github.ps1  [-Repo Tanishqnarayan/ScholarSeek-]
param([string]$Repo = "Tanishqnarayan/ScholarSeek-")

$ErrorActionPreference = "Continue"

# Ensure gh CLI is reachable in this session even when PATH is stale
# (e.g. terminal opened before the PATH update or winget install).
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  $fallback = "C:\Program Files\GitHub CLI\gh.exe"
  if (Test-Path $fallback) { $env:Path = "C:\Program Files\GitHub CLI;" + $env:Path }
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  Write-Host "gh CLI not found. Install it (winget install --id GitHub.cli -e), restart the terminal, then re-run." -ForegroundColor Red
  return
}
function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# 1. Labels ----------------------------------------------------------------
Step "Creating labels"
$labels = @(
  @("feature", "0e8a16", "New functionality"),
  @("bug", "d73a4a", "Something is broken"),
  @("testing", "fbca04", "Tests and QA"),
  @("documentation", "0075ca", "Docs and Agile artifacts"),
  @("sprint-1", "1d76db", "Sprint 1: document processing and indexing"),
  @("sprint-2", "5319e7", "Sprint 2: search and ranking"),
  @("sprint-3", "0e8a16", "Sprint 3: Django application"),
  @("sprint-4", "e99695", "Sprint 4: testing, CI/CD, finalization"),
  @("priority-critical", "b60205", "Critical priority"),
  @("priority-high", "d93f0b", "High priority"),
  @("priority-medium", "fbca04", "Medium priority"),
  @("priority-low", "0e8a16", "Low priority")
)
foreach ($l in $labels) {
  gh label create $l[0] --color $l[1] --description $l[2] --repo $Repo 2>$null
  if ($LASTEXITCODE -ne 0) { gh label edit $l[0] --color $l[1] --description $l[2] --repo $Repo 2>$null }
}
Write-Host "labels ok"

# 2. Issues -----------------------------------------------------------------
Step "Creating 12 user-story issues"
$issues = @(
  @("US-01 Add academic documents", "feature,sprint-1,sprint-3,priority-critical",
    "As a user, I want to add academic documents so that they become searchable.`n`nStory points: 5 | Priority: Critical | Sprints: 1, 3`n`nAcceptance:`n- Upload .txt via /manage/ (staff), reject non-.txt / empty / >2MB`n- Invalid files skipped with a clear message, index rebuilt automatically`n- Files: search_app/views.py (manage), search_app/management/commands/rebuild_index.py"),
  @("US-02 Preprocess documents", "feature,sprint-1,priority-critical",
    "As the system, I want to preprocess documents so that text can be indexed consistently.`n`nStory points: 3 | Priority: Critical | Sprint: 1`n`nAcceptance:`n- Pipeline: lowercase, punctuation removal, whitespace norm, tokenize, stop-word + invalid-token filter`n- 'Python is a high-level programming language.' -> [python, high, level, programming, language]`n- Files: search_engine/preprocessor.py"),
  @("US-03 Inverted index", "feature,sprint-1,priority-critical",
    "As the system, I want to build an inverted index so that documents can be retrieved efficiently.`n`nStory points: 5 | Priority: Critical | Sprint: 1`n`nAcceptance:`n- dict[str, set[doc_id]] postings, no duplicate doc refs, term frequencies kept`n- JSON save/load round-trips without loss (data/index.json)`n- Files: search_engine/indexer.py"),
  @("US-04 Search documents", "feature,sprint-2,priority-critical",
    "As a user, I want to search academic documents so that I can find relevant information.`n`nStory points: 5 | Priority: Critical | Sprint: 2`n`nAcceptance:`n- Single + multi-term queries, case-insensitive, stop-word-safe`n- Empty query returns no results (no crash)`n- Files: search_engine/query_parser.py, search_engine/engine.py"),
  @("US-05 Rank by relevance", "feature,sprint-2,priority-critical",
    "As a user, I want search results ranked by relevance so that the best results appear first.`n`nStory points: 8 | Priority: Critical | Sprint: 2`n`nAcceptance:`n- Hand-written TF-IDF (tf=1+ln freq, smoothed idf) + coverage boost, never random order`n- `database normalization` ranks dbms.txt first at 100.0%`n- Files: search_engine/ranker.py"),
  @("US-06 Result snippets", "feature,sprint-2,priority-high",
    "As a user, I want to see relevant snippets so that I can understand why a result matched.`n`nStory points: 3 | Priority: High | Sprint: 2`n`nAcceptance:`n- Snippet window prefers phrase/term hits, falls back to doc start`n- Query terms highlighted with <mark>`n- Files: search_engine/snippets.py"),
  @("US-07 Phrase search", "feature,sprint-2,sprint-3,priority-high",
    'As a user, I want phrase search so that I can search exact expressions.`n`nStory points: 3 | Priority: High | Sprints: 2, 3`n`nAcceptance:`n- `"deadlock detection"` returns os.txt first with phrase-match flag + 1.5x boost`n- Files: search_engine/query_parser.py, search_engine/engine.py'),
  @("US-08 Boolean search", "feature,sprint-3,priority-high",
    "As a user, I want Boolean search so that I can make advanced queries.`n`nStory points: 5 | Priority: High | Sprint: 3`n`nAcceptance:`n- AND = intersect, OR = union, NOT = subtract; `python NOT django` excludes python.txt`n- Results paginated (5/page)`n- Files: search_engine/query_parser.py, search_app/views.py"),
  @("US-09 Search history", "feature,sprint-3,priority-medium",
    "As a user, I want my search history saved so that I can review previous searches.`n`nStory points: 3 | Priority: Medium | Sprint: 3`n`nAcceptance:`n- Every search persists SearchQuery + ranked SearchResults in MySQL`n- /history/ lists recent queries with top hits`n- Files: search_app/models.py, search_app/views.py"),
  @("US-10 Automated tests", "testing,sprint-2,sprint-4,priority-high",
    "As a developer, I want automated tests so that changes do not break existing functionality.`n`nStory points: 5 | Priority: High | Sprints: 2, 4`n`nAcceptance:`n- 39 unit tests (preprocess, loader, index, search, ranking, phrases, booleans, edge cases)`n- 9 Django tests (views, history, pagination); all green on MySQL`n- Files: tests/, search_app/tests.py"),
  @("US-11 CI checks", "documentation,sprint-4,priority-medium",
    "As a developer, I want CI checks to run automatically when code is pushed.`n`nStory points: 3 | Priority: Medium | Sprint: 4`n`nAcceptance:`n- .github/workflows/python-tests.yml runs on push/PR: unit tests, migrate, rebuild_index, Django tests`n- Workflow fails closed on any test failure`n- Files: .github/workflows/python-tests.yml"),
  @("US-12 Web interface", "feature,sprint-3,priority-high",
    "As a user, I want a clean web interface so that searching is easy.`n`nStory points: 5 | Priority: High | Sprint: 3`n`nAcceptance:`n- Pages: home (popular searches), results (relevance bars), document, history, staff manage`n- Plain HTML/CSS, no frontend framework`n- Files: search_app/templates/, search_app/static/")
)
$urls = @()
$existingMap = @{}
$existingJson = gh issue list --repo $Repo --state all --limit 100 --json title,url 2>$null
if ($LASTEXITCODE -eq 0) {
  foreach ($e in ($existingJson | ConvertFrom-Json)) { $existingMap[$e.title] = $e.url }
} else {
  Write-Host "Cannot list issues - check 'gh auth status'. Re-login if needed." -ForegroundColor Yellow
}
foreach ($i in $issues) {
  if ($existingMap.ContainsKey($i[0])) {
    $urls += $existingMap[$i[0]]; Write-Host "exists, reusing: $($i[0])"
    continue
  }
  $out = gh issue create --repo $Repo --title $i[0] --label $i[1] --body $i[2] --format json -q ".url" 2>&1
  if ($LASTEXITCODE -eq 0) { $urls += $out.Trim(); Write-Host "created: $($i[0])" }
  else { Write-Host "FAILED: $($i[0]) -- $out" -ForegroundColor Red }
}
Write-Host "`n$($urls.Count) of 12 issues ready."

# 3. Project board ------------------------------------------------------------
Step "Creating project board 'ScholarSeek Kanban'"
$owner = $Repo.Split("/")[0]
$projNumber = $null
$projJson = gh project create --owner $owner --title "ScholarSeek Kanban" --format json 2>&1
if ($LASTEXITCODE -eq 0) {
  $projNumber = ($projJson | ConvertFrom-Json).number
  Write-Host "project #$projNumber created."
} else {
  Write-Host "Project create failed: $projJson" -ForegroundColor Yellow
  if ($projJson -match "scopes") {
    Write-Host 'Fix: run  gh auth refresh -s project,read:project  then re-run this script.' -ForegroundColor Yellow
    return
  }
  $list = gh project list --owner $owner --format json 2>$null
  if ($LASTEXITCODE -eq 0) {
    $hit = ($list | ConvertFrom-Json).projects | Where-Object { $_.title -eq "ScholarSeek Kanban" } | Select-Object -First 1
    if ($hit) { $projNumber = $hit.number; Write-Host "reusing existing project #$projNumber." }
  }
  if (-not $projNumber) {
    Write-Host "Open https://github.com/users/$owner/projects and add the 12 issues manually."
    return
  }
}
$already = @()
$items = gh project item-list $projNumber --owner $owner --format json 2>$null
if ($LASTEXITCODE -eq 0) {
  foreach ($it in ($items | ConvertFrom-Json).items) {
    if ($it.content.url) { $already += $it.content.url }
  }
}
foreach ($u in $urls) {
  if ($already -contains $u) { continue }
  gh project item-add $projNumber --owner $owner --url $u 2>$null | Out-Null
}
Write-Host "items added. Finishing: set all cards to Done + rename columns in the board UI:"
Write-Host "  https://github.com/users/$($Repo.Split('/')[0])/projects/$projNumber/views/1"
Write-Host "  Columns to use: BACKLOG | TODO | IN PROGRESS | CODE REVIEW | TESTING | DONE"
