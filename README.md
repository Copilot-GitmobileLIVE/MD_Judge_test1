# MD_Judge Agent Plugin

This project packages `MD_Judge`, a custom LLM judge agent for evaluating `MD_Test`.

If your main agent workspace was renamed to `MD_Main_Agent`, treat that folder as the source for the packaged `MD_Test` agent when using the judge.

The bundled judge agent is designed to:

- collaborate with `MD_Test` when the host platform supports custom-agent delegation
- evaluate `MD_Test` outputs against the user's request
- score the evaluated agent on a 0-10 rubric
- save scoring artifacts under `Scoring_Results\<evaluated_agent_name>_YYYYMMDD_HHMMSS_scoring`

The Python package can scaffold scoring folders and run a complete evaluation workflow directly.

## Install

```powershell
pip install -e .
```

## Commands

Show the bundled agent definition:

```powershell
md-judge-agent show
```

Install the agent into another workspace:

```powershell
md-judge-agent install --target-dir C:\path\to\other-workspace
```

Export the raw agent file anywhere:

```powershell
md-judge-agent export --output C:\temp\MD_Judge.agent.md
```

Create a timestamped scoring folder for an evaluated agent:

```powershell
md-judge-agent init-score --evaluated-agent-name MD_Main_Agent --output-root .
```

This creates a folder like:

```text
Scoring_Results\md_main_agent_YYYYMMDD_HHMMSS_scoring\
```

Run the evaluation and write the completed scoring files in one command:

```powershell
md-judge-agent evaluate --target-workspace C:\Users\GhobadNarimani\Agents\MD_Main_Agent --evaluated-agent-name MD_Main_Agent --output-root .
```

If you want a command name that makes the test step explicit, use:

```powershell
md-judge-agent test-and-evaluate --target-workspace C:\Users\GhobadNarimani\Agents\MD_Main_Agent --evaluated-agent-name MD_Main_Agent --output-root .
```

If you prefer calling the module directly:

```powershell
python -m md_judge_agent_plugin.cli evaluate --target-workspace C:\Users\GhobadNarimani\Agents\MD_Main_Agent --evaluated-agent-name MD_Main_Agent --output-root .
```

Overwrite an existing installed or generated output:

```powershell
md-judge-agent install --target-dir C:\path\to\other-workspace --force
md-judge-agent init-score --evaluated-agent-name MD_Main_Agent --output-root . --force
md-judge-agent evaluate --target-workspace C:\Users\GhobadNarimani\Agents\MD_Main_Agent --evaluated-agent-name MD_Main_Agent --output-root . --force
md-judge-agent test-and-evaluate --target-workspace C:\Users\GhobadNarimani\Agents\MD_Main_Agent --evaluated-agent-name MD_Main_Agent --output-root . --force
```

## What gets installed

The installer writes:

```text
.github\agents\MD_Judge.agent.md
```

inside the target workspace.

## Scoring bundle layout

The scoring helper creates:

```text
<output-root>\Scoring_Results\<evaluated_agent_name>_YYYYMMDD_HHMMSS_scoring\
```

with these files:

- `manifest.json`
- `scoring_summary.json`
- `scoring_notes.md`

The `evaluate` and `test-and-evaluate` commands both run `python -m unittest discover -s tests -v` in the target workspace and write the completed score, rubric breakdown, and evidence into those files automatically.

For example, from the MD_Judge_Agent workspace root, a completed evaluation is saved under:

```text
Scoring_Results\md_main_agent_YYYYMMDD_HHMMSS_scoring\
```

with these generated files:

- `manifest.json`: evaluated agent metadata, task summary, and reviewed evidence
- `scoring_summary.json`: final score, pass/fail result, rubric maximums, and rubric scores
- `scoring_notes.md`: strengths, weaknesses, reviewed evidence, and recommendations

## Testing

Run the MD_Judge_Agent test suite:

```powershell
python -m unittest discover -s tests -v
```

This command only runs the automated tests. It does not save evaluation output under `Scoring_Results`.

The scoring tests use temporary directories and clean them up after the test run, so you should not expect a persistent folder to appear in the repository when running `python -m unittest discover -s tests -v`.

If you want a real saved evaluation result under `Scoring_Results`, run:

```powershell
python -m md_judge_agent_plugin.cli evaluate --target-workspace C:\Users\GhobadNarimani\Agents\MD_Main_Agent --evaluated-agent-name MD_Main_Agent --output-root .
```

Or use the clearer alias:

```powershell
python -m md_judge_agent_plugin.cli test-and-evaluate --target-workspace C:\Users\GhobadNarimani\Agents\MD_Main_Agent --evaluated-agent-name MD_Main_Agent --output-root .
```

Then inspect the newest saved folder with:

```powershell
Get-ChildItem .\Scoring_Results -Directory |
	Sort-Object LastWriteTime -Descending |
	Select-Object -First 1 FullName
```

## Notes

This package ships the judge agent in the VS Code custom agent format. The agent definition instructs the host to collaborate with `MD_Test` when that environment supports inter-agent execution, and to treat the renamed `MD_Main_Agent` workspace as that agent's source when relevant. The Python CLI focuses on packaging and scoring-artifact scaffolding.
# MD_Judge_test1
