from fhirclient.models.patient import Patient
from phenopackets import Individual, OntologyClass, VitalStatus
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
import logging


class FhirPatient:
    @staticmethod
    def to_individual(patient: Patient) -> Individual:
        """
        Maps a FHIR Patient resource to a Phenopacket Subject.
        """
        kwargs = {}
        kwargs["id"] = patient.id if patient.id else "unknown-patient"
        sex_map = {"male": "MALE", "female": "FEMALE", "other": "OTHER_SEX", "unknown": "UNKNOWN_SEX"}
        kwargs["sex"] = sex_map.get(patient.gender if patient.gender else "unknown", "UNKNOWN_SEX")
        kwargs["taxonomy"] = OntologyClass(id="NCBITaxon:9606", label="Homo sapiens")
        kwargs["vital_status"] = VitalStatus(status="DECEASED") if patient.deceasedBoolean else VitalStatus(status="ALIVE")
        if patient.birthDate is not None:
            try:
                dt = datetime.strptime(str(patient.birthDate), "%Y-%m-%d")
                ts = Timestamp()
                ts.FromDatetime(dt)
                kwargs["date_of_birth"] = ts
            except Exception as e:
                logging.warning(f"Could not parse birthDate '{patient.birthDate}': {e}")
        return Individual(**kwargs)