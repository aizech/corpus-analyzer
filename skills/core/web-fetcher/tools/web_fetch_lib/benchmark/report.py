"""Generate JSON/Markdown benchmark reports."""

import json
from pathlib import Path
from statistics import mean


def _avg(values: list[float]) -> float:
    return round(mean(values), 2) if values else 0.0


def _build_summary_table(results: list[dict]) -> str:
    """Build a per-engine summary Markdown table."""
    per_engine: dict[str, list[dict]] = {}
    for entry in results:
        for run in entry.get("runs", []):
            engine = run.get("engine", "unknown")
            per_engine.setdefault(engine, []).append(run)

    lines = [
        "| Engine | Success rate | Avg time (ms) | Avg chars | Avg headings | Avg boilerplate |",
        "|--------|--------------|---------------|-----------|--------------|-----------------|",
    ]
    for engine, runs in sorted(per_engine.items()):
        successes = [r for r in runs if r.get("success")]
        success_rate = len(successes) / len(runs) if runs else 0.0
        avg_time = _avg([r.get("elapsed_ms", 0) for r in successes])
        avg_chars = _avg([r.get("chars", 0) for r in successes])
        avg_headings = _avg([r.get("headings", 0) for r in successes])
        avg_boilerplate = _avg([r.get("boilerplate_score", 0) for r in successes])
        lines.append(
            f"| {engine} | {success_rate:.0%} | {avg_time} | {avg_chars:.0f} | "
            f"{avg_headings:.1f} | {avg_boilerplate:.4f} |"
        )

    return "\n".join(lines)


def generate_markdown(data: dict) -> str:
    """Convert benchmark data into a readable Markdown report."""
    lines = [
        "# web_fetch Benchmark Report",
        "",
        f"**Dataset:** {data.get('dataset', 'unknown')}",
        f"**Runs per URL/engine:** {data.get('runs_per_url', 1)}",
        f"**Total URLs:** {len(data.get('results', []))}",
        "",
        "## Engine Summary",
        "",
        _build_summary_table(data.get("results", [])),
        "",
        "## Per-URL Results",
        "",
    ]

    for entry in data.get("results", []):
        lines.append(f"### {entry['id']} ({entry['url']})")
        lines.append(f"Category: {entry.get('category', 'unknown')}")
        lines.append("")
        lines.append("| Engine | Success | Time (ms) | Chars | Headings | Boilerplate | Cached |")
        lines.append("|--------|---------|-----------|-------|----------|-------------|--------|")
        for run in entry.get("runs", []):
            if run.get("success"):
                lines.append(
                    f"| {run.get('engine', 'unknown')} | yes | {run.get('elapsed_ms', 0)} | "
                    f"{run.get('chars', 0)} | {run.get('headings', 0)} | "
                    f"{run.get('boilerplate_score', 0)} | {run.get('cached', False)} |"
                )
            else:
                engine_name = run.get("engine", "unknown")
                elapsed = run.get("elapsed_ms", 0)
                lines.append(f"| {engine_name} | no | {elapsed} | - | - | - | - |")
        lines.append("")

    return "\n".join(lines)


def write_reports(data: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "web_fetch_benchmark.json"
    md_path = output_dir / "web_fetch_benchmark.md"
    json_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    md_path.write_text(generate_markdown(data), encoding="utf-8")
