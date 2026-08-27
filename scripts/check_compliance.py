"""Compliance Verification Audit for Nexus Frontier Repository & Zip Package."""
import os
import subprocess
import zipfile

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ZIP_PATH = os.path.join(SRC, "Game Development.zip")


def run_audit():
    # 1. Count Production LOC
    prod_loc = 0
    prod_files = 0
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', '.venv', 'venv', 'tests', 'node_modules', 'dist', 'build']]
        for f in files:
            if f.endswith('.py') and not f.startswith('test_'):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    prod_loc += len([l for l in fp if l.strip()])
                    prod_files += 1

    # 2. Check Git History & PR Merges
    log = subprocess.check_output(['git', 'log', '--oneline'], cwd=SRC, text=True).strip().splitlines()
    merges = [l for l in log if 'Merge pull request' in l or 'Merge branch' in l]

    # 3. Check Zip Package & .git Presence
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        zip_files = z.namelist()
        has_git_in_zip = any(f.startswith('.git') for f in zip_files)

    # 4. Check Proprietary License
    with open(os.path.join(SRC, 'LICENSE'), 'r', encoding='utf-8') as f:
        lic = f.read()
        is_proprietary = 'PROPRIETARY' in lic and 'MIT' not in lic and 'Apache' not in lic

    # 5. Check Lockfiles
    has_locks = os.path.exists(os.path.join(SRC, 'requirements.lock')) and os.path.exists(os.path.join(SRC, 'poetry.lock'))

    print("=" * 65)
    print("           TRAINPLEX / REPO COMPLIANCE AUDIT")
    print("=" * 65)
    print(f"1. Minimum 50,000+ Prod LOC : {prod_loc:,} lines across {prod_files} files -> {'PASS' if prod_loc >= 50000 else 'FAIL'}")
    print(f"2. Git Repository in Zip    : {len([f for f in zip_files if f.startswith('.git')])} git objects -> {'PASS' if has_git_in_zip else 'FAIL'}")
    print(f"3. Minimum 5+ Commits       : {len(log)} commits recorded -> {'PASS' if len(log) >= 5 else 'FAIL'}")
    print(f"4. Minimum 4+ Pull Requests : {len(merges)} PR merges -> {'PASS' if len(merges) >= 4 else 'FAIL'}")
    print(f"5. Proprietary License      : Proprietary (No OS License) -> {'PASS' if is_proprietary else 'FAIL'}")
    print(f"6. Manifests & Lockfiles    : requirements.lock + poetry.lock -> {'PASS' if has_locks else 'FAIL'}")
    print(f"7. Total Zip Package Files  : {len(zip_files)} total files")
    print("=" * 65)


if __name__ == "__main__":
    run_audit()
