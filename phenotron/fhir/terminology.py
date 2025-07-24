from typing import Optional
from phenopackets.schema.v2.core.base_pb2 import OntologyClass


class TerminologyMapper:
    """
    Handles mapping between different medical terminologies.
    This is a simplified stub. A production system would use a robust terminology service.
    """

    def __init__(self):
        # Example mappings from SNOMED CT to HPO and MONDO
        self.snomed_to_hpo_map = {
            "39065001": ("HP:0000822", "Hypertension"),
            "44054006": ("HP:0005978", "Type II diabetes mellitus"),
            "363406005": ("HP:0001250", "Seizure"),
        }
        self.snomed_to_mondo_map = {
            "44054006": ("MONDO:0005148", "type 2 diabetes mellitus"),
            "73211009": ("MONDO:0005177", "epilepsy"),
        }
        self.loinc_to_hpo_map = {
            # This mapping is conceptual: the LOINC code is for the test,
            # the HPO is for the interpretation.
            "8480-6": ("HP:0000822", "Hypertension"),  # Systolic Blood Pressure
        }

    def get_hpo_from_snomed(self, snomed_code: str) -> Optional[OntologyClass]:
        """Maps a SNOMED CT code to an HPO term."""
        if snomed_code in self.snomed_to_hpo_map:
            hpo_id, label = self.snomed_to_hpo_map[snomed_code]
            return OntologyClass(id=hpo_id, label=label)
        return None

    def get_mondo_from_snomed(self, snomed_code: str) -> Optional[OntologyClass]:
        """Maps a SNOMED CT code to a MONDO term."""
        if snomed_code in self.snomed_to_mondo_map:
            mondo_id, label = self.snomed_to_mondo_map[snomed_code]
            return OntologyClass(id=mondo_id, label=label)
        return None

    def get_hpo_from_loinc(self, loinc_code: str) -> Optional[OntologyClass]:
        """Maps a LOINC code to a conceptual HPO phenotype."""
        if loinc_code in self.loinc_to_hpo_map:
            hpo_id, label = self.loinc_to_hpo_map[loinc_code]
            return OntologyClass(id=hpo_id, label=label)
        return None

