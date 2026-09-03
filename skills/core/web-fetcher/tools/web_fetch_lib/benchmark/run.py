"""Run the web_fetch engine benchmark."""

import argparse
import asyncio
import os
import time
from pathlib import Path
from typing import Any

import yaml
from web_fetch_lib.benchmark.metrics import compute_error_metrics, compute_metrics
from web_fetch_lib.benchmark.report import write_reports
from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines import ENGINES

_DEFAULT_DATASET = Path(__file__).resolve().parents[3] / "tests" / "benchmark" / "urls.yaml"
_DEFAULT_OUTPUT = Path("outputs")


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    entries = data.get("entries", [])
    for entry in entries:
        if not entry.get("id"):
            entry["id"] = entry["url"].replace("://", "_").replace("/", "_")[:80]
    return entries


def _is_live_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def _resolve_fixture_url(url: str, dataset_dir: Path) -> str:
    """Resolve relative fixture paths against the dataset directory."""
    if url.startswith("file://"):
        return url
    if Path(url).is_absolute() or (dataset_dir / url).exists():
        resolved = Path(url) if Path(url).is_absolute() else dataset_dir / url
        return resolved.resolve().as_uri()
    return url


async def _run_engine(entry: dict, engine_name: str) -> dict:
    engine = ENGINES[engine_name]
    ctx = FetchContext(
        url=entry["url"],
        render_js=engine.requires_browser,
        timeout=30.0,
        browser_wait_until="networkidle",
    )
    start = time.perf_counter()
    try:
        result = await engine.fetch(ctx)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return compute_metrics(result, elapsed_ms)
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return compute_error_metrics(exc, elapsed_ms)


async def _benchmark_entry(entry: dict, engine_names: list[str], runs: int) -> dict:
    runs_data = []
    for name in engine_names:
        engine = ENGINES[name]
        if not engine.supports_url(entry["url"]):
            continue
        for _ in range(runs):
            runs_data.append({"engine": name, **await _run_engine(entry, name)})
    return {
        "id": entry["id"],
        "url": entry["url"],
        "category": entry.get("category", "unknown"),
        "description": entry.get("description", ""),
        "runs": runs_data,
    }


async def run_benchmark(
    dataset_path: Path,
    output_dir: Path,
    engine_names: list[str] | None,
    runs: int,
    skip_live: bool,
) -> dict:
    entries = _load_dataset(dataset_path)
    dataset_dir = dataset_path.parent
    engine_names = list(engine_names or ENGINES.keys())

    filtered: list[dict[str, Any]] = []
    for entry in entries:
        url = _resolve_fixture_url(entry["url"], dataset_dir)
        entry["url"] = url
        if skip_live and _is_live_url(url):
            continue
        filtered.append(entry)

    results = []
    for entry in filtered:
        print(f"Benchmarking: {entry['id']} ({entry['url']})")
        results.append(await _benchmark_entry(entry, engine_names, runs))

    report = {
        "dataset": str(dataset_path),
        "runs_per_url": runs,
        "engines": engine_names,
        "results": results,
    }
    write_reports(report, output_dir)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark web_fetch engines.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=_DEFAULT_DATASET,
        help="Path to the YAML dataset of URLs/fixtures",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help="Directory to write benchmark reports",
    )
    parser.add_argument(
        "--engines",
        nargs="+",
        default=None,
        help="Engines to benchmark (default: all)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs per URL/engine",
    )
    parser.add_argument(
        "--skip-live",
        action="store_true",
        help="Skip live HTTP(S) URLs and only run local fixtures",
    )
    args = parser.parse_args()

    skip_live = args.skip_live or not os.environ.get("RUN_LIVE_TESTS")
    asyncio.run(
        run_benchmark(
            dataset_path=args.dataset,
            output_dir=args.output,
            engine_names=args.engines,
            runs=args.runs,
            skip_live=skip_live,
        )
    )
    print(f"Reports written to {args.output / 'web_fetch_benchmark.json'}")
    print(f"Markdown report at {args.output / 'web_fetch_benchmark.md'}")


if __name__ == "__main__":
    main()
