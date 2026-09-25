from app.services.icai_catalog import ICAI_CATALOG


def test_icai_catalog_contains_current_chapterwise_pdf_links() -> None:
    assert len(ICAI_CATALOG) >= 100
    assert len({(item["title"], item["source"]) for item in ICAI_CATALOG}) == len(ICAI_CATALOG)
    assert any(
        item["level"] == "CA Intermediate"
        and item["subject"] == "Advanced Accounting"
        and "Chapter 15" in item["chapter"]
        and item["source"].endswith(".pdf")
        for item in ICAI_CATALOG
    )
    assert any(
        item["level"] == "CA Foundation"
        and item["subject"] == "Business Laws"
        and "Unit 9" in item["chapter"]
        and item["source"].endswith(".pdf")
        for item in ICAI_CATALOG
    )
