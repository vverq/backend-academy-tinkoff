import os

import pytest

HTTP_404_ERROR_TEXT = "Пришел 404, скорее всего ничего не нашли\n"


def test_output(capfd):
    os.system("python -m tv_program.py Family Guy")
    out, err = capfd.readouterr()
    expected = (
        "Name: Family Guy\n"
        "Network Name: FOX\n"
        "Network Country Name: United States\n"
        "Summary: <p><b>Family Guy</b> follows Peter Griffin the "
        "endearingly ignorant dad, and his hilariously offbeat family "
        "of middle-class New Englanders in Quahog, RI. Lois is "
        "Peter's wife, a stay-at-home mom with no patience for her "
        "family's antics. Then there are their kids: 18-year-old Meg "
        "is an outcast at school and the Griffin family punching bag; "
        "13-year-old Chris is a socially awkward teen who doesn't "
        "have a clue about the opposite sex; and one-year-old Stewie "
        "is a diabolically clever baby whose burgeoning sexuality is "
        "very much a work in progress. Rounding out the Griffin "
        "household is Brian the family dog and a ladies' man who is "
        "one step away from AA.</p>\n"
    )
    assert expected == out.replace("\r", "")


def test_search_by_prefix(capfd):
    os.system("python -m tv_program.py The")
    out, err = capfd.readouterr()
    expected = (
        "Name: The Rookie\n"
        "Network Name: ABC\n"
        "Network Country Name: United States\n"
        "Summary: <p><b>The Rookie</b> is inspired by a true story. "
        "John Nolan is the oldest rookie in the LAPD. At an age where "
        "most are at the peak of their career, Nolan cast aside his "
        "comfortable, small town life and moved to L.A. to pursue his "
        "dream of being a cop. Now, surrounded by rookies twenty years "
        "his junior, Nolan must navigate the dangerous, humorous and "
        'unpredictable world of a "young" cop, determined to make his '
        "second shot at life count.</p>\n"
    )
    assert expected == out.replace("\r", "")


def test_search_by_suffix(capfd):
    os.system("python -m tv_program.py bang theory")
    out, err = capfd.readouterr()
    expected = (
        "Name: The Big Bang Theory\n"
        "Network Name: CBS\n"
        "Network Country Name: United States\n"
        "Summary: <p><b>The Big Bang Theory</b> is a comedy about brilliant "
        "physicists, Leonard and Sheldon, who are the kind of "
        '"beautiful minds" that understand how the universe works. '
        "But none of that genius helps them interact with people, "
        "especially women. All this begins to change when a free-spirited "
        "beauty named Penny moves in next door. Sheldon, Leonard's roommate, "
        "is quite content spending his nights playing Klingon Boggle with "
        "their socially dysfunctional friends, fellow Cal Tech scientists "
        "Wolowitz and Koothrappali. However, Leonard sees in Penny a whole "
        "new universe of possibilities... including love.</p>\n"
    )
    assert expected == out.replace("\r", "")


def test_search_nonexistent(capfd):
    os.system("python -m tv_program.py abcdef")
    out, err = capfd.readouterr()
    assert HTTP_404_ERROR_TEXT == out.replace("\r", "")


@pytest.mark.parametrize("search_str", [" ", "'"])
def test_search_invalid_string(capfd, search_str):
    os.system(f"python -m tv_program.py {search_str}")
    out, err = capfd.readouterr()
    assert HTTP_404_ERROR_TEXT == out.replace("\r", "")
