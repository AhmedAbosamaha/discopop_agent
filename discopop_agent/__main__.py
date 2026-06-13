import os
from pathlib import Path

from .args import parse_args
from .controller import run


def _load_dotenv() -> None:
    """Load .env from the project root without any extra dependencies.

    Keys loaded: LLM_API_KEY (and any other entries in the file).
    Already-set env vars are never overwritten (setdefault semantics).
    """
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> None:
    _load_dotenv()
    run(parse_args())


if __name__ == "__main__":
    main()
