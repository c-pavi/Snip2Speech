from snip2speech.speech_text import prepare_for_speech


def test_bullet_lines_each_end_with_a_pause():
    text = "Items:\n• First thing\n• Second thing\n• Third thing"
    assert prepare_for_speech(text) == "Items: First thing. Second thing. Third thing."


def test_ocr_misread_bullet_letters_are_removed():
    text = "e Several rare leaks were closed\n\ne Keyboard shortcuts work again"
    out = prepare_for_speech(text)
    assert "e Several" not in out and "e Keyboard" not in out
    assert "Several rare leaks were closed." in out
    assert "Keyboard shortcuts work again." in out


def test_ordinary_words_starting_with_e_or_o_are_kept():
    assert prepare_for_speech("every day\nonly once").startswith("every day")


def test_screen_wrapped_sentence_stays_one_sentence():
    text = "This build focuses on stability and correctness. We fixed a crash that happened when\nopening a document from a network volume."
    out = prepare_for_speech(text)
    assert "happened when opening a document" in out
    assert out.count(".") == 2  # no spurious pause added at the wrap


def test_heading_without_punctuation_gets_a_pause():
    out = prepare_for_speech("Release notes\nThis build focuses on stability.")
    assert out == "Release notes. This build focuses on stability."


def test_unpunctuated_list_items_get_pauses():
    text = "Play sound for incoming alerts On\nShow previews only when unlocked On\nBadge the app icon Off"
    out = prepare_for_speech(text)
    assert out == "Play sound for incoming alerts On. Show previews only when unlocked On. Badge the app icon Off."


def test_paragraphs_stay_separated():
    out = prepare_for_speech("First paragraph.\n\nSecond paragraph.")
    assert out == "First paragraph.\n\nSecond paragraph."


def test_existing_punctuation_is_not_doubled():
    assert prepare_for_speech("Done.\nReally?\nYes!") == "Done. Really? Yes!"


def test_empty_input():
    assert prepare_for_speech("") == ""
    assert prepare_for_speech("  \n \n") == ""
