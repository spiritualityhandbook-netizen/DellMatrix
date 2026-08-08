#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

COMMANDS = [
    ("git_status", ["git", "status", "--short", "--untracked-files=all"]),
    ("audit_smoke", ["python3", "-m", "form.smoke_all"]),
    ("english_brain_150", ["python3", "-m", "form.mandell.english_brain_150_loop"]),
    ("program_evolve_150", ["python3", "-m", "form.dell_matrix.program_evolve_150_loop", "--cycles", "150"]),
    ("function_150", ["python3", "-m", "form.dell_matrix.function_150_loop", "--cycles", "150"]),
    ("page_enhance_150", ["python3", "-m", "form.dell_matrix.page_enhance_loop", "--cycles", "150"]),
    ("button_path_enhance_150", ["python3", "-m", "form.dell_matrix.button_path_enhance_loop", "--cycles", "150"]),
    ("visual_evolve_150", ["python3", "-m", "form.dell_matrix.visual_evolve_loop", "--cycles", "150"]),
    ("sync_ux_150", ["python3", "-m", "form.dell_matrix.sync_ux_150_loop", "--cycles", "150"]),
]

OUTPUT_PATH = Path("audit_and_enhance_report.json")


def run_command(name, command):
    print(f"Running {name}: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        status = 0
    except subprocess.CalledProcessError as exc:
        result = exc
        status = exc.returncode
    return {
        "name": name,
        "command": command,
        "returncode": status,
        "stdout": result.stdout if hasattr(result, "stdout") else "",
        "stderr": result.stderr if hasattr(result, "stderr") else "",
    }


def main():
    report = {"runs": []}
    for name, cmd in COMMANDS:
        report["runs"].append(run_command(name, cmd))
        report["last_run"] = report["runs"][-1]["name"]
        with OUTPUT_PATH.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    print(f"Audit and enhancement report saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
