#!/usr/bin/env python3
"""Generate a daily deposit report for the external brain.

Usage:
  python3 tools/deposit_report.py
  python3 tools/deposit_report.py --write
  python3 tools/deposit_report.py --root /path/to/my-brain --write

It only reads file names and git metadata; it never reads private/ contents.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
from pathlib import Path

SKIP_DIRS = {
    ".git",
    "private",
    "__pycache__",
    "node_modules",
    "reports",
    ".venv",
    "venv",
}


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            yield Path(dirpath, filename)


def modified_today(root: Path):
    today = dt.date.today()
    result = []
    for path in iter_files(root):
        try:
            modified = dt.date.fromtimestamp(path.stat().st_mtime)
        except OSError:
            continue
        if modified == today:
            result.append(path.relative_to(root).as_posix())
    return sorted(result)


def run_git(root: Path, args):
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if completed.returncode == 0:
            return completed.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def build_report(root: Path):
    today = dt.date.today().isoformat()
    files = modified_today(root)
    git_status = run_git(root, ["status", "--short"])
    git_log = run_git(root, ["log", "--since", "midnight", "--pretty=format:%h %s"])

    lines = [
        f"# 沉淀日报 · {today}",
        "",
        "> 只列文件名和 git 元数据，不读 private/ 内容。",
        "",
        "## 今日改动",
        "",
    ]

    if files:
        lines.extend(f"- `{path}`" for path in files)
    else:
        lines.append("- 今天没有文件改动。")

    lines += ["", "## Git 状态", "", "```", git_status or "（无未提交改动）", "```"]
    lines += ["", "## 今日提交", "", git_log or "（今天没有提交）"]
    lines += [
        "",
        "## 需要你确认",
        "",
        "- [ ] 今天记的内容，哪些该留在 `wiki/`？",
        "- [ ] 有没有该进 `private/` 的？",
        "- [ ] `private/待定/` 有没有要复查的？",
        "",
        "## 今日一句",
        "",
        "〔今天最有价值的一条结论，自己写〕",
        "",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a daily deposit report.")
    parser.add_argument(
        "--root",
        default=".",
        help="Path to the brain repo (default: current directory).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the report to reports/YYYY-MM-DD.md.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_report(root)
    print(report)

    if args.write:
        reports_dir = root / "reports"
        reports_dir.mkdir(exist_ok=True)
        output = reports_dir / f"{dt.date.today().isoformat()}.md"
        output.write_text(report + "\n", encoding="utf-8")
        print(f"\n已写入 {output}")


if __name__ == "__main__":
    main()
