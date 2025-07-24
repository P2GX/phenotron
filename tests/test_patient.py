import pytest
from phenotron.fhir._patient import FhirPatient
from fhirclient.models.patient import Patient
from phenopackets import VitalStatus, Sex
from google.protobuf.timestamp_pb2 import Timestamp
def make_patient(id=None, gender=None, birthDate=None, deceasedBoolean=None):
    patient = Patient()
    if id is not None:
        patient.id = id
    if gender is not None:
        patient.gender = gender
    if birthDate is not None:
        patient.birthDate = birthDate
    if deceasedBoolean is not None:
        patient.deceasedBoolean = deceasedBoolean
    return patient

@pytest.mark.parametrize(
    "id, gender, birthDate, deceasedBoolean, expected_status, expected_sex, expected_dob_none",
    [
        ("123", "male", "1980-01-01", False, "ALIVE", "MALE", False),
        ("456", "female", "1970-05-15", True, "DECEASED", "FEMALE", False),
        ("789", "other", None, False, "ALIVE", "OTHER_SEX", True),
        ("000", None, "2000-12-31", False, "ALIVE", "UNKNOWN_SEX", False),
    ]
)
def test_to_individual(id, gender, birthDate, deceasedBoolean, expected_status, expected_sex, expected_dob_none):
    patient = make_patient(id=id, gender=gender, birthDate=birthDate, deceasedBoolean=deceasedBoolean)
    individual = FhirPatient.to_individual(patient)
    assert VitalStatus.Status.Name(individual.vital_status.status) == expected_status
    assert individual.id == id
    assert Sex.Name(individual.sex) == expected_sex
    assert individual.taxonomy.id == "NCBITaxon:9606"
    if expected_dob_none:
        # Empty timestamp
        assert individual.date_of_birth == Timestamp()
    else:
        assert individual.date_of_birth is not None