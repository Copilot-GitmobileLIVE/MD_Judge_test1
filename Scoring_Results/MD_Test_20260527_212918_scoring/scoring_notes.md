# Scoring Notes — MD_Test Evaluation

**Evaluated agent:** MD_Test  
**Task:** Create a `CONTRIBUTING.md` for the MD_Judge_Agent_Plugin Python project  
**Date:** 2026-05-27  
**Total score:** 8 / 10 — **PASS**

---

## Strengths

- **Complete coverage.** All five requested sections were produced: introduction, dev-environment
  setup, test-suite instructions, coding guidelines, and PR-submission steps.
- **Project-aware.** The agent consulted `pyproject.toml` to surface the correct Python version
  (≥ 3.11) and confirmed editable install as the right install command.
- **Readable markdown.** Numbered top-level sections, properly fenced code blocks with `bash`
  language tags, and horizontal rules make the file easy to navigate.
- **Transparent reasoning.** The agent declared which files it read before writing, allowing
  the judge to verify the evidence chain.

---

## Weaknesses

- **Test-runner mismatch.** The project's own README and CLI documentation consistently use
  `python -m unittest discover -s tests -v`. MD_Test led with `pytest` (not a declared
  dependency) and relegated `unittest` to an alternative. This could cause confusion for
  first-time contributors.
- **Unverified commit claim.** The agent said it "created and committed" the file. In a
  background agent context this action could not be confirmed. The agent should have qualified
  this claim (e.g., "here is the content to save as `CONTRIBUTING.md`") or noted the
  limitation explicitly.
- **No safety/limitations flag.** When an action (file commit) cannot be confirmed in the
  agent's execution environment, best practice is to state that limitation rather than assert
  success. Omitting this reduces trust in the output.

---

## File-by-File Findings

| File | Finding |
|------|---------|
| `CONTRIBUTING.md` (proposed) | Content is accurate and well-structured. Minor: pytest listed as primary runner; project standard is unittest. |
| Agent reasoning block | Good — cited `pyproject.toml`, `tests/`, and `README` explicitly. |
| Commit claim | Unverifiable — should be qualified. |

---

## Recommendations

1. **Align test instructions with project standard.** Change the primary command to
   `python -m unittest discover -s tests -v` (matching the README), and mention `pytest`
   only as an optional alternative.
2. **Qualify file-write and commit claims.** When running in an environment where file I/O
   success is uncertain, say "here is the file content" rather than "I have committed this."
3. **Add a dependency note.** Since `pytest` is not in `pyproject.toml`, contributing docs
   should not assume contributors have it installed unless it is added as a dev dependency.
