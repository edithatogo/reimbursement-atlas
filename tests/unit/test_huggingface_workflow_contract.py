from pathlib import Path

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
