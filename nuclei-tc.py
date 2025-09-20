#!/usr/bin/env python3
import os
import re
import requests
import shutil
import subprocess
import yaml
import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

REPO_FILE = "repos.txt"
BASE_DIR = "community-templates"
CATEGORY_FILE = "categories.json"

def safe_dirname(url: str) -> str:
    """Make safe folder name for repo"""
    return url.strip().lower().replace("https://", "").replace("/", "__")

def clone_or_update_repo(url, index, total):
    """Clone or update repo with progress. Skip if 404 or authentication is required."""
    repo_name = "/".join(url.split("/")[-2:])
    target_dir = os.path.join(BASE_DIR, safe_dirname(url))
    os.makedirs(BASE_DIR, exist_ok=True)

    # Step 1: Check if the repo URL exists (HTTP HEAD)
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        if resp.status_code == 404:
            console.print(f"[!] Skipped {repo_name} (404 Not Found)")
            return
        if resp.status_code in [401, 403]:
            console.print(f"[!] Skipped {repo_name} (Authentication/Forbidden)")
            return
    except requests.RequestException:
        console.print(f"[!] Skipped {repo_name} (Network error)")
        return

    # Step 2: Determine clone or pull
    if os.path.exists(target_dir):
        cmd = ["git", "-C", target_dir, "pull", "--progress"]
        action = "Updating"
    else:
        cmd = ["git", "clone", "--progress", "--depth", "1", url, target_dir]
        action = "Cloning"

    # Step 3: Clone or pull with progress
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"[{index:03}/{total:03}] {action} {repo_name}", total=100)
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)

        skipped = False
        for line in process.stderr:
            # Detect git authentication errors
            if "Authentication failed" in line or "Repository not found" in line or "fatal: could not read Username" in line:
                console.print(f"[!] Skipped {repo_name} (requires authentication)")
                process.kill()
                skipped = True
                break

            match = re.search(r"(\d+)%", line)
            if match:
                progress.update(task, completed=int(match.group(1)))

        if not skipped:
            process.wait()
            progress.update(task, completed=100)
def scan_templates(source_dir):
    """Scan all YAML templates under source_dir"""
    template_list = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith((".yaml", ".yml")):
                template_list.append(os.path.join(root, file))
    return template_list

def remove_duplicates(template_list):
    """Remove duplicate templates by filename"""
    seen = {}
    duplicates = 0
    unique_templates = []
    for tpl in template_list:
        fname = os.path.basename(tpl)
        if fname in seen:
            duplicates += 1
        else:
            seen[fname] = tpl
            unique_templates.append(tpl)
    return unique_templates, duplicates

def categorize_template_tags(tags, category_map):
    """Determine the category for a template based on tags"""
    if isinstance(tags, str):
        tags = [t.strip().lower() for t in tags.split(",")]
    elif isinstance(tags, list):
        tags = [t.lower() for t in tags]
    else:
        tags = []

    for cat, keywords in category_map.items():
        if any(k in tags for k in keywords):
            return cat
    return "other"

def organize_by_category(template_list, category_map, base_dir):
    """Move templates into folders by category"""
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Organizing templates", total=len(template_list))
        for tpl in template_list:
            try:
                with open(tpl, "r", errors="ignore") as f:
                    data = yaml.safe_load(f)
                info_tags = data.get("info", {}).get("tags", []) if isinstance(data, dict) else []
                category = categorize_template_tags(info_tags, category_map)
                dest_dir = os.path.join(base_dir, category)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy(tpl, os.path.join(dest_dir, os.path.basename(tpl)))
            except Exception:
                category = "other"
            progress.update(task, advance=1)

def categorize_templates(template_list, category_map):
    """Count templates in each category based on tags"""
    counts = {cat: 0 for cat in category_map}
    counts["other"] = 0

    for tpl in template_list:
        try:
            with open(tpl, "r", errors="ignore") as f:
                data = yaml.safe_load(f)
            info_tags = data.get("info", {}).get("tags", []) if isinstance(data, dict) else []
            category = categorize_template_tags(info_tags, category_map)
            counts[category] += 1
        except Exception:
            counts["other"] += 1
    return counts

def show_summary(counts):
    """Display category counts and percentages"""
    total = sum(counts.values())
    from rich.table import Table
    table = Table(title="Template Categorization Summary")
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Percent", justify="right", style="magenta")
    for cat, count in sorted(counts.items(), key=lambda x: -x[1]):
        percent = 0 if total == 0 else round(count / total * 100, 1)
        table.add_row(cat, str(count), f"{percent}%")
    console.print(table)
    console.print(f"TOTAL: {total}")

def cleanup_repo_folders(base_dir):
    """Remove cloned GitHub repo folders after templates are organized"""
    repo_folders = [d for d in os.listdir(base_dir) if d.startswith("github.com__")]
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Removing repo folders", total=len(repo_folders))
        for item in repo_folders:
            path = os.path.join(base_dir, item)
            try:
                shutil.rmtree(path)
            except Exception as e:
                console.print(f"[!] Failed to remove {item}: {e}")
            progress.update(task, advance=1)

def main():
    if not os.path.exists(REPO_FILE):
        console.print(f"[!] Repo file {REPO_FILE} not found!")
        return
    if not os.path.exists(CATEGORY_FILE):
        console.print(f"[!] Category mapping file {CATEGORY_FILE} not found!")
        return

    with open(REPO_FILE) as f:
        repos = [line.strip() for line in f if line.strip()]

    with open(CATEGORY_FILE) as f:
        category_map = json.load(f)

    console.print(f"[*] Starting clone/update for {len(repos)} repos\n")
    for idx, repo in enumerate(repos, 1):
        clone_or_update_repo(repo, idx, len(repos))

    console.print("\n[*] Scanning templates and counting duplicates...\n")
    all_templates = scan_templates(BASE_DIR)
    unique_templates, duplicates = remove_duplicates(all_templates)
    console.print(f"[✓] Scanned {len(all_templates)} templates, removed {duplicates} duplicates.\n")

    console.print("[*] Organizing templates by category...\n")
    organize_by_category(unique_templates, category_map, BASE_DIR)

    console.print("[*] Categorizing templates...\n")
    counts = categorize_templates(unique_templates, category_map)

    console.print("[*] Cleaning up cloned repo folders...\n")
    cleanup_repo_folders(BASE_DIR)
    show_summary(counts)

if __name__ == "__main__":
    main()
