from typing import Dict, Any, Tuple
from phenopackets import Phenopacket, PhenotypicFeature, Disease, MetaData, Resource, OntologyClass
from phenopackets.schema.v2.core.individual_pb2 import Individual
from fhirclient.models.patient import Patient
from .terminology import TerminologyMapper
from .observation import ObservationInterpreter
import datetime
from ._patient import FhirPatient

class FhirConverter:
    """
    Orchestrates the conversion of a FHIR Bundle to a GA4GH Phenopacket.
    """

    def __init__(self, terminology_mapper: TerminologyMapper):
        self.terminology_mapper = terminology_mapper
        self.interpreter = ObservationInterpreter(terminology_mapper)

    def convert_patient(self, patient: Patient):
        """
        Extracts patient data from the source.
        """

        subject = FhirPatient.to_individual(patient)
        # map observations
        return Phenopacket(id=subject.id, subject=subject, phenotypic_features=[])

    # def convert_all_patients(self, fhir_bundle: Dict[str, Any]) -> Phenopacket:
    #     """
    #     Main conversion method.

    #     Args:
    #         fhir_bundle: A FHIR Bundle as a Python dictionary.

    #     Returns:
    #         A Phenopacket object.
    #     """
    #     patient_resource = self._find_resource(fhir_bundle, "Patient")
    #     if not patient_resource:
    #         raise ValueError("No Patient resource found in the FHIR bundle.")

    #     subject = self._map_patient_to_subject(patient_resource)

    #     phenotypic_features = []
    #     diseases = []

    #     for entry in fhir_bundle.get("entry", []):
    #         resource = entry.get("resource", {})
    #         resource_type = resource.get("resourceType")

    #         if resource_type == "Condition":
    #             feature, disease = self._map_condition(resource)
    #             if feature:
    #                 phenotypic_features.append(feature)
    #             if disease:
    #                 diseases.append(disease)

    #         elif resource_type == "Observation":
    #             feature = self.interpreter.interpret_observation(resource)
    #             if feature:
    #                 phenotypic_features.append(feature)

    #     # Create the phenopacket
    #     phenopacket = Phenopacket(
    #         id=f"phenopacket-for-{subject.id}",
    #         subject=subject,
    #         phenotypic_features=phenotypic_features,
    #         diseases=diseases,
    #         meta_data=self._create_metadata()
    #     )
    #     return phenopacket

    # def _find_resource(self, bundle: Dict[str, Any], resource_type: str) -> Optional[Dict[str, Any]]:
    #     """Finds the first resource of a given type in a bundle."""
    #     for entry in bundle.get("entry", []):
    #         resource = entry.get("resource", {})
    #         if resource.get("resourceType") == resource_type:
    #             return resource
    #     return None

    # def _map_condition(self, condition: Dict[str, Any]) -> Tuple[Optional[PhenotypicFeature], Optional[Disease]]:
    #     """
    #     Maps a FHIR Condition to a PhenotypicFeature and/or a Disease.
    #     A condition might be a primary diagnosis (Disease) or a sign/symptom (Phenotype).
    #     """
    #     snomed_code = condition.get("code", {}).get("coding", [{}])[0].get("code")
    #     if not snomed_code:
    #         return None, None

    #     # Strategy: First, check if it's a known disease (MONDO). If not, treat as a phenotype (HPO).
    #     disease_term = self.terminology_mapper.get_mondo_from_snomed(snomed_code)
    #     if disease_term:
    #         disease = Disease(term=disease_term)
    #         if condition.get("onsetDateTime"):
    #             disease.onset.timestamp = condition["onsetDateTime"]
    #         return None, disease

    #     phenotype_term = self.terminology_mapper.get_hpo_from_snomed(snomed_code)
    #     if phenotype_term:
    #         feature = PhenotypicFeature(type=phenotype_term)

    #         # Handle negation
    #         verification_status = condition.get("verificationStatus", {}).get("coding", [{}])[0].get("code")
    #         if verification_status == "refuted":
    #             feature.excluded = True

    #         # Handle onset
    #         if condition.get("onsetDateTime"):
    #             feature.onset.timestamp = condition["onsetDateTime"]

    #         return feature, None

    #     return None, None

    # def _create_metadata(self) -> MetaData:
    #     """Creates the metadata block for the phenopacket."""
    #     return MetaData(
    #         created=datetime.datetime.now().isoformat() + "Z",
    #         created_by="FhirToPhenopacketConverter-v1.0",
    #         resources=[
    #             Resource(id="hp", name="Human Phenotype Ontology", url="http://purl.obolibrary.org/obo/hp.owl",
    #                      version="2023-10-09", namespace_prefix="HP"),
    #             Resource(id="mondo", name="Monarch Disease Ontology", url="http://purl.obolibrary.org/obo/mondo.owl",
    #                      version="2023-10-02", namespace_prefix="MONDO"),
    #             Resource(id="snomed", name="SNOMED CT", url="http://snomed.info/sct", version="2023-09-07",
    #                      namespace_prefix="SCTID"),
    #         ]
    #     )

