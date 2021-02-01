"""
Test single anonymization steps
"""
import pytest
from verbatim_anonymizer.anonymize_verbatim_file import (
    AnonymizerSteps,
    anonymize_verbatim,
)
from verbatim_anonymizer.anonmization_steps import (
    BlacklistAnonymizationStep,
    DEFAULT_ANONYMIZATION_PIPELINE,
)


@pytest.mark.parametrize(
    "text,query,not_in",
    [
        ("Contact me: +41791234567", "791234567", True),
        ("Contact me: +41791234567", "Contact me", False),
        ("+41 79 123 45 67 or 079 123 45 67", "79 123 45 67", True),
        ("079-123-45-67", "079", True),
        ("complained 4 times", "complained 4 times", False),
        ("Had to drive 400km", "400km", False),
        ("Had to drive 1'400km", "1'400km", False),
        ("Had to pay 400€", "400€", False),
        ("Had to pay 1'400€", "1'400€", False),
        ("This is the case since 01/02/2020", "01/02/2020", False),
    ],
)
def test_phone_number_anonymizer(text, query, not_in):
    ex = AnonymizerSteps.phone_number(text)
    if not_in:
        assert query not in ex
    else:
        assert query in ex


@pytest.mark.parametrize(
    "text,query,not_in",
    [
        ("Auftrag Nr A4312-1234", "A4312-1234", True),
        ("Auftrag Nr 4312123AB", "4312123AB", True),
        ("complained 4 times", "complained 4 times", False),
        ("Had to drive 400km", "400km", False),
        ("Had to drive 1'400km", "1'400km", False),
        ("Had to pay 400€", "400€", False),
        ("Had to pay 1'400€", "1'400€", False),
        ("This is the case since 01/02/2020", "01/02/2020", False),
    ],
)
def test_contract_number_anonymizer(text, query, not_in):
    ex = AnonymizerSteps.contract_number(text)
    if not_in:
        assert query not in ex
    else:
        assert query in ex


@pytest.mark.parametrize(
    "text,query,not_in",
    [
        ("test@gmail.com", AnonymizerSteps.email.value.replace_value, False),
        ("Contact me at test@test.test or call me", "test@test.test", True),
    ],
)
def test_email_anonymizer(text, query, not_in):
    ex = AnonymizerSteps.email(text)
    if not_in:
        assert query not in ex
    else:
        assert query in ex


@pytest.mark.parametrize(
    "text,query,not_in",
    [
        ("John Doe did something amazing", "John Doe", True),
        (
            "Fantastic job by Ms Catherine Panizo-Alvarez",
            "Catherine Panizo-Alvarez",
            True,
        ),
    ],
)
def test_entity_anonymizer(text, query, not_in):
    ex = AnonymizerSteps.person(text)
    if not_in:
        assert query not in ex
    else:
        assert query in ex


def test_replace_value_cleaner():
    repl_val = (
        AnonymizerSteps.duplicate_replace_value_cleaner.value.replace_value
    )
    ex_1 = "{} {}".format(repl_val, repl_val)
    assert len(AnonymizerSteps.duplicate_replace_value_cleaner(ex_1)) == len(
        repl_val
    )


def test_blacklist():
    step = BlacklistAnonymizationStep(["asd"], "...")
    ex_1 = step("dies ist asd")
    assert "asd" not in ex_1


@pytest.mark.parametrize(
    "text,queries,not_in",
    [
        (
            "Please contact me at test@gmail.com, +41 79 123 34 56, my name is Peter Parker",
            ["test@gmail.com", "+41 79 123 34 56", "Peter Parker"],
            True,
        ),
        (
            "Ms Catherine Parker did a great job, send her my regards, best, Peter Parker",
            ["Catherine Parker", "Peter Parker"],
            True,
        ),
    ],
)
def test_default_anonymizer(text, queries, not_in):
    ex = anonymize_verbatim(text, DEFAULT_ANONYMIZATION_PIPELINE)
    for query in queries:
        if not_in:
            assert query not in ex
        else:
            assert query in ex
