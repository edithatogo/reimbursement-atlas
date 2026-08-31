import os
import shlex
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "huggingface.yml"


def test_huggingface_push_uses_supported_token_auth_without_secret_url() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert workflow.count('export HF_USERNAME="${HF_') == 2
    assert workflow.count("*Username*) printf '%s\\n' \"$HF_USERNAME\" ;;") == 2
    assert "https://hf:${HF_TOKEN}@huggingface.co" not in workflow
    assert "config http.https://huggingface.co/.extraheader" not in workflow
    assert workflow.count('GIT_ASKPASS="$RUNNER_TEMP/hf-askpass"') >= 4


def test_dataset_staging_preserves_and_refreshes_software_licence() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "rsync -av --delete --exclude='.git/' infra/huggingface/ hf-dataset/" not in workflow
    assert "cp LICENSE hf-dataset/LICENSE" in workflow


def test_dataset_clone_skips_lfs_payloads_without_changing_raw_tree_or_space() -> None:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    dataset = next(
        step["run"]
        for step in workflow["jobs"]["publish-dataset"]["steps"]
        if step.get("name") == "Push dataset artefacts to Hugging Face Hub"
    )
    space = next(
        step["run"]
        for step in workflow["jobs"]["publish-space"]["steps"]
        if step.get("name") == "Push dashboard to Hugging Face Space"
    )
    assert (
        'GIT_LFS_SKIP_SMUDGE=1 git -c http.extraheader="Authorization: Bearer $HF_TOKEN" '
        '\\\n  clone "https://huggingface.co/datasets/${HF_DATASET_REPO}" hf-dataset'
    ) in dataset
    assert "GIT_LFS_SKIP_SMUDGE" not in space
    assert "--delete" not in dataset
    assert "hf-dataset/raw" not in dataset
    assert "uv run python scripts/stage_huggingface_medallion.py hf-dataset" in dataset
    assert "git add ." in dataset


def publication_push(job: str) -> list[str]:
    """Extract the actual workflow push so the local race test exercises its flags."""
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    script = next(
        step["run"]
        for step in workflow["jobs"][job]["steps"]
        if step.get("name", "").startswith("Push ")
    )
    pushes = [
        shlex.split(line[line.index("git push ") :])
        for line in script.replace("\\\n", " ").splitlines()
        if "git push " in line
    ]
    assert pushes == [["git", "push", "origin", "HEAD:main"]]
    assert "--force" not in script
    return pushes[0]


@pytest.mark.parametrize("job", ["publish-dataset", "publish-space"])
def test_publication_push_is_non_forcing(job: str) -> None:
    publication_push(job)


@pytest.mark.parametrize("job", ["publish-dataset", "publish-space"])
@pytest.mark.parametrize("concurrent_update", [False, True])
def test_publication_push_preserves_concurrent_remote_commit(
    tmp_path: Path, job: str, concurrent_update: bool
) -> None:
    """Even after a fresh fetch, a stale publisher cannot overwrite remote additions."""

    def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "git",
                "-c",
                "user.name=Workflow Test",
                "-c",
                "user.email=test@example.invalid",
                "-c",
                "commit.gpgsign=false",
                "-c",
                f"core.hooksPath={os.devnull}",
                *args,
            ],
            cwd=cwd,
            env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"},
            check=check,
            capture_output=True,
            text=True,
        )

    remote, writer, publisher = (tmp_path / name for name in ("remote.git", "writer", "publisher"))
    git(tmp_path, "init", "--bare", "--initial-branch=main", str(remote))
    git(tmp_path, "clone", str(remote), str(writer))
    (writer / "README.md").write_text("Initial synthetic fixture\n")
    git(writer, "add", ".")
    git(writer, "commit", "-m", "Initial fixture")
    git(writer, "push", "origin", "HEAD:main")
    git(tmp_path, "clone", str(remote), str(publisher))
    (publisher / "derived.txt").write_text("Proposed publication\n")
    git(publisher, "add", ".")
    git(publisher, "commit", "-m", "Proposed publication")

    protected = "raw/pbs/concurrent.txt" if job == "publish-dataset" else "user-deploy.txt"
    if concurrent_update:
        addition = writer / protected
        addition.parent.mkdir(parents=True, exist_ok=True)
        addition.write_text("Concurrent synthetic fixture\n")
        git(writer, "add", ".")
        git(writer, "commit", "-m", "Concurrent remote update")
        git(writer, "push", "origin", "HEAD:main")
    remote_before = git(remote, "rev-parse", "main").stdout.strip()
    git(publisher, "fetch", "origin", "main")
    assert git(publisher, "rev-parse", "FETCH_HEAD").stdout.strip() == remote_before
    result = git(publisher, *publication_push(job)[1:], check=False)
    if concurrent_update:
        assert result.returncode != 0
        assert git(remote, "rev-parse", "main").stdout.strip() == remote_before
        assert git(remote, "show", f"main:{protected}").stdout == "Concurrent synthetic fixture\n"
        assert git(remote, "cat-file", "-e", "main:derived.txt", check=False).returncode != 0
    else:
        assert result.returncode == 0, result.stderr
        assert git(remote, "rev-parse", "main").stdout == git(publisher, "rev-parse", "HEAD").stdout
        assert git(remote, "show", "main:derived.txt").stdout == "Proposed publication\n"
