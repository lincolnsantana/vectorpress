from app.core.config import parse_csv_env


def test_parse_csv_env_removes_empty_items_and_spaces() -> None:
    origins = parse_csv_env("https://app.example.com, https://admin.example.com, ,")

    assert origins == ["https://app.example.com", "https://admin.example.com"]
