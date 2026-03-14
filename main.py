"""
main.py
-------
CLI entry point for the NeuraX Project Assignment Agent.

Usage:
  # Run a specific project by ID from the bundled data file:
  python main.py --id PRJ001

  # Run with a custom project JSON file:
  python main.py --file path/to/project.json

  # Pass a project as a raw JSON string:
  python main.py --json '{"project_id":"PRJ001", ...}'

  # Run as importable module from the NeuraX orchestrator:
  from main import run_agent
  result = run_agent(project_dict)
"""

import argparse
import json
import sys
from agent import config
from agent.models import ProjectInput

DATA_PROJECTS_PATH = config.DATA_DIR / "projects.json"


def run_agent(project: dict, output_dir: str = "output", verbose: bool = True) -> dict:
    """
    Module-mode entry point. Import and call this from upstream NeuraX agents.

    Args:
        project: project dict
        output_dir: where to write reports
        verbose: print progress logs

    Returns:
        Full result dict from planner_agent.run_pipeline()
    """
    from agent.planner_agent import run_pipeline
    return run_pipeline(project, output_dir=output_dir, verbose=verbose)


def _load_project_by_id(project_id: str) -> dict:
    with open(DATA_PROJECTS_PATH, "r", encoding="utf-8") as f:
        projects = json.load(f)
    for p in projects:
        if p["project_id"] == project_id:
            return p
    raise ValueError(f"Project ID '{project_id}' not found in {DATA_PROJECTS_PATH}")


def main():
    parser = argparse.ArgumentParser(
        description="NeuraX Project Assignment Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--id", help="Project ID from data/projects.json (e.g. PRJ001)")
    group.add_argument("--file", help="Path to a JSON file containing a single project dict")
    group.add_argument("--json", help="Raw JSON string of the project dict")

    parser.add_argument(
        "--output",
        default="output",
        help="Output directory for reports (default: ./output)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress logs; only print the final Markdown report",
    )

    args = parser.parse_args()

    # Load and validate project
    if args.id:
        project_dict = _load_project_by_id(args.id)
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            project_dict = json.load(f)
    else:
        project_dict = json.loads(args.json)
    
    # Validate with Pydantic
    project_model = ProjectInput(**project_dict)
    project = project_model.model_dump()

    # Run pipeline
    result = run_agent(project, output_dir=args.output, verbose=not args.quiet)

    # Print final Markdown to stdout
    print("\n" + result["markdown"])
    print(f"\n✅ Reports saved to: {args.output}/")


if __name__ == "__main__":
    main()
