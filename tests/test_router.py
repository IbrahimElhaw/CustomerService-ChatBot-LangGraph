import pytest

from support_bot.agents.router import rule_based_route


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Ich will mit einem Mitarbeiter sprechen", "human"),
        ("Wie hoch sind die Versandkosten?", None),
        ("Wo ist meine Bestellung SN-1001?", None),
    ],
)
def test_rule_based_route(text, expected):
    assert rule_based_route(text) == expected