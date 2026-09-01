from snip2speech.table import try_parse_as_table


def test_tab_separated_table_detected():
    text = "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\n"
    df = try_parse_as_table(text)
    assert df is not None
    assert df.shape == (3, 3)


def test_aligned_columns_detected():
    text = (
        "Name       Age   City\n"
        "Alice      30    NYC\n"
        "Bob        25    LA\n"
    )
    df = try_parse_as_table(text)
    assert df is not None
    assert df.shape[1] == 3
    assert df.shape[0] == 3


def test_prose_is_not_detected_as_table():
    text = (
        "This is a normal paragraph of text.\n"
        "It has  a couple of  double spaces in it.\n"
        "But it is not a table at all.\n"
    )
    assert try_parse_as_table(text) is None


def test_short_text_is_not_a_table():
    assert try_parse_as_table("Just one line") is None
    assert try_parse_as_table("Two\nLines") is None


def test_empty_text_is_not_a_table():
    assert try_parse_as_table("") is None
    assert try_parse_as_table("   \n  \n") is None
