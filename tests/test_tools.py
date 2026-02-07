from agentic_ai.tools import GoogleProgrammableSearchTool, SearchResult, extract_year, pick_top_recent


def test_extract_year() -> None:
    assert extract_year("Paper 2024 on crop yield") == 2024
    assert extract_year("No year") is None


def test_pick_top_recent() -> None:
    rows = [
        SearchResult("old paper", "u1", "research", 2021),
        SearchResult("new paper", "u2", "research", 2025),
        SearchResult("mid paper", "u3", "research", 2023),
    ]
    top = pick_top_recent(rows, k=2)
    assert [x.year for x in top] == [2025, 2023]


def test_google_search_returns_empty_without_credentials() -> None:
    tool = GoogleProgrammableSearchTool(api_key="", cse_id="")
    assert tool.search("ai agriculture", max_results=3) == []
