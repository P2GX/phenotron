import pytest
from fhirclient.models.condition import Condition
from phenopackets import Disease, PhenotypicFeature

from phenotron.fhir import FhirConverter, TerminologyMapper
from phenotron.fhir._condition import (
    HPO_SYSTEM,
    MONDO_SYSTEM,
    SNOMED_SYSTEM,
    ConditionInterpreter,
)


def make_condition(system=None, code=None, display=None):
    """Builds a minimal FHIR Condition with a single coding, or no code if system and code are None."""
    data = {"resourceType": "Condition", "subject": {"reference": "Patient/1"}}
    if system is not None or code is not None:
        coding = {"system": system, "code": code}
        if display is not None:
            coding["display"] = display
        data["code"] = {"coding": [coding]}
    return Condition(data)


@pytest.fixture
def interpreter():
    return ConditionInterpreter(TerminologyMapper())


@pytest.mark.parametrize(
    "system, code, display, expected_type, expected_id",
    [
        # In both MONDO and HPO maps: MONDO wins
        (SNOMED_SYSTEM, "44054006", None, Disease, "MONDO:0005148"),
        # MONDO map only
        (SNOMED_SYSTEM, "73211009", None, Disease, "MONDO:0005177"),
        # HPO map only
        (SNOMED_SYSTEM, "39065001", None, PhenotypicFeature, "HP:0000822"),
        (HPO_SYSTEM, "HP:0001250", "Seizure", PhenotypicFeature, "HP:0001250"),
        (MONDO_SYSTEM, "MONDO:0005177", "epilepsy", Disease, "MONDO:0005177"),
    ],
)
def test_interpret_mapped(interpreter, system, code, display, expected_type, expected_id):
    result = interpreter.interpret(make_condition(system, code, display))
    assert isinstance(result, expected_type)
    term = result.term if isinstance(result, Disease) else result.type
    assert term.id == expected_id


@pytest.mark.parametrize(
    "system, code",
    [
        (SNOMED_SYSTEM, "000000"),
        ("http://loinc.org", "8480-6"),
        (None, None),
    ],
)
def test_interpret_unmapped_returns_none(interpreter, system, code):
    assert interpreter.interpret(make_condition(system, code)) is None


def test_convert_conditions_skips_uncoded():
    fc = FhirConverter(TerminologyMapper())
    features = fc.convert_conditions(
        [make_condition(SNOMED_SYSTEM, "39065001"), make_condition()]
    )
    assert len(features) == 1
    assert isinstance(features[0], PhenotypicFeature)
