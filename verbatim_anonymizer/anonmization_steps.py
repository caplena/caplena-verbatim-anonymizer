"""
Components for creating an anonymization pipeline
"""

import re
from enum import Enum
from typing import Sequence


DEFAULT_REPLACE_VALUE = "(...)"


class Languages(str, Enum):
    de = "de"
    en = "en"


LANGUAGE_TO_MODEL = {
    Languages.de: "de_core_news_lg",
    Languages.en: "en_core_web_lg",
}


class AnonymizationStep(object):
    def __call__(self, text: str) -> str:
        return text


class BlacklistAnonymizationStep(AnonymizationStep):
    def __init__(self, blacklist: Sequence[str], replace_value: str):
        self.blacklist = blacklist
        self.replace_value = replace_value

    def __call__(self, text: str):
        for el in self.blacklist:
            text = text.replace(el, self.replace_value)
        return text


class RegexAnoymizationStep(AnonymizationStep):
    def __init__(
        self,
        regex: str,
        replace_value: str,
        translate: bool = False,
        ignore_case: bool = True,
    ):
        self.regex = re.compile(
            regex, flags=re.IGNORECASE if ignore_case else 0
        )
        self.replace_value = replace_value
        self.translate = translate

    def __call__(self, text: str):
        if self.translate:
            matches = self.regex.finditer(text)
            if not matches:
                pass
            else:
                for match in matches:
                    text = (
                        text[: match.start()]
                        + self.replace_value * len(match.group())
                        + text[match.end() :]
                    )
        else:
            text = self.regex.sub(self.replace_value, text)
        return text


class NamedEntities(str, Enum):
    person = "PER"
    person_onto = "PERSON"
    location = "LOC"
    organization = "ORG"
    miscellaneous = "MISC"


class EntityAnonymizerStep(AnonymizationStep):
    """
    Uses spacy entity recognition to identify
    and anonymize named entities such as names,
    organizations and locations
    """

    def __init__(
        self,
        entities: Sequence[NamedEntities],
        replace_value: str,
        exclude=None,
        language=Languages.en,
    ):
        import spacy

        self.entities = entities
        self.replace_value = replace_value
        if exclude:
            self.exclude = exclude
        else:
            self.exclude = {}

        self.nlp = spacy.load(LANGUAGE_TO_MODEL[language])
        merge_ents = self.nlp.create_pipe("merge_entities")
        self.nlp.add_pipe(merge_ents)

    def __call__(self, text):
        doc = self.nlp(text)
        out = []
        for sent in doc.sents:
            for i, t in enumerate(sent):
                exclude_not_matches = [
                    excl not in t.text.lower().split(" ")
                    for excl in self.exclude
                ]
                if (t.ent_type_ in self.entities) and all(exclude_not_matches):
                    # add a whitespace to replace value to compensate for potentially removing
                    # it as part of the token
                    replace_val = (
                        self.replace_value + " "
                        if t.whitespace_
                        else self.replace_value
                    )
                    # if it's only a single capitalized word at the
                    # beginning of the sentence, keep it as it was
                    # often observed as a false positive
                    is_single_first_cap_word = (
                        i == 0
                        and t.text[0].isupper()
                        and len(t.text.split(" ")) == 1
                    )
                    if is_single_first_cap_word:
                        out.append(t.text_with_ws)
                    else:
                        out.append(replace_val)
                else:
                    out.append(t.text_with_ws)
        out = "".join(out)
        return out


class AnonymizerSteps(Enum):
    person = EntityAnonymizerStep(
        entities=[NamedEntities.person, NamedEntities.person_onto],
        replace_value=DEFAULT_REPLACE_VALUE,
        exclude={},
    )
    organization = EntityAnonymizerStep(
        entities=[NamedEntities.organization],
        replace_value=DEFAULT_REPLACE_VALUE,
    )
    location = EntityAnonymizerStep(
        entities=[NamedEntities.location], replace_value=DEFAULT_REPLACE_VALUE
    )
    email = RegexAnoymizationStep(
        regex=r"(\S+|\S+\s)@(\s\S+|\S+)(\.|\s\.)(\S+|\s\S+)",
        replace_value="abc@xyz.de",
        ignore_case=True,
    )
    phone_number = RegexAnoymizationStep(
        regex=r"[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}([\s-]{0,1}[0-9]{2,}){2,}($|[\s\,\.])",
        replace_value=r"{}\g<2>".format(DEFAULT_REPLACE_VALUE),
        ignore_case=False,
        translate=False,
    )
    contract_number = RegexAnoymizationStep(
        regex=r"(?=.*[0-9])(?=.*[A-Z])([A-ZÄÖÜ0-9-]{5,})",
        replace_value="x",
        ignore_case=False,
        translate=True,
    )
    spaces_cleaner = RegexAnoymizationStep(regex=r"\s{2,}", replace_value=" ")
    duplicate_replace_value_cleaner = RegexAnoymizationStep(
        regex=r"{}\W({})+".format(
            re.escape(DEFAULT_REPLACE_VALUE), re.escape(DEFAULT_REPLACE_VALUE)
        ),
        replace_value=DEFAULT_REPLACE_VALUE,
    )
    blacklist = BlacklistAnonymizationStep(
        blacklist=[], replace_value=DEFAULT_REPLACE_VALUE
    )

    def __call__(self, *args, **kwargs):
        return self.value.__call__(*args, **kwargs)


DEFAULT_ANONYMIZATION_PIPELINE = [
    AnonymizerSteps.spaces_cleaner,
    AnonymizerSteps.person,
    AnonymizerSteps.contract_number,
    AnonymizerSteps.phone_number,
    AnonymizerSteps.email,
    AnonymizerSteps.duplicate_replace_value_cleaner,
    AnonymizerSteps.blacklist,
]
