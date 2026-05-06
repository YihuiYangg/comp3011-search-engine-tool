from src.indexer import build_index, extract_visible_text, tokenize, Document


def test_tokenize_is_case_insensitive_and_keeps_positions_ready_tokens():
    assert tokenize("Good, good FRIENDS don't shout!") == [
        "good",
        "good",
        "friends",
        "don't",
        "shout",
    ]


def test_extract_visible_text_ignores_script_and_style_content():
    html = """
    <html><head><style>.hidden{}</style><script>alert('x')</script></head>
    <body><h1>Hello</h1><p>Visible text.</p></body></html>
    """
    text = extract_visible_text(html)
    assert "Hello" in text
    assert "Visible text" in text
    assert "alert" not in text
    assert "hidden" not in text


def test_build_index_records_frequency_and_positions():
    documents = [
        Document("https://example.test/", "<p>Good friends, good books.</p>"),
        Document("https://example.test/about/", "<p>Good ideas.</p>"),
    ]
    index = build_index(documents)

    assert index["good"]["https://example.test/"]["frequency"] == 2
    assert index["good"]["https://example.test/"]["positions"] == [0, 2]
    assert index["friends"]["https://example.test/"]["frequency"] == 1
    assert index["good"]["https://example.test/about/"]["positions"] == [0]
