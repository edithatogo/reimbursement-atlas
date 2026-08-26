from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "huggingface.yml"


def test_huggingface_push_uses_supported_token_auth_without_secret_url() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert workflow.count("*Username*) printf '%s\\n' \"__token__\" ;;") == 2
    assert "https://hf:${HF_TOKEN}@huggingface.co" not in workflow
    assert workflow.count('GIT_ASKPASS="$RUNNER_TEMP/hf-askpass"') >= 4


def test_dataset_staging_preserves_and_refreshes_software_licence() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "rsync -av --delete --exclude='.git/' infra/huggingface/ hf-dataset/" not in workflow
    assert "cp LICENSE hf-dataset/LICENSE" in workflow
