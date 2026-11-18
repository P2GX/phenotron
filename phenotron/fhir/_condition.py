from typing import Optional, Union

from fhirclient.models.condition import Condition
from phenopackets import Disease, OntologyClass, PhenotypicFeature

from .terminology import TerminologyMapper

SNOMED_SYSTEM = "http://snomed.info/sct"
HPO_SYSTEM = "http://purl.obolibrary.org/obo/hp.owl"
MONDO_SYSTEM = "http://purl.obolibrary.org/obo/mondo.owl"


class ConditionInterpreter:
    """
    Maps FHIR Condition resources to Phenopacket Disease or PhenotypicFeature messages.

    Args:
        terminology_mapper: Mapper used to translate SNOMED CT codes to MONDO and HPO terms.
    """

    def __init__(self, terminology_mapper: TerminologyMapper):
        self.terminology_mapper = terminology_mapper

    def interpret(self, condition: Condition) -> Optional[Union[Disease, PhenotypicFeature]]:
        """
        Maps a FHIR Condition to a Disease or PhenotypicFeature based on its first coding.

        SNOMED CT codes map to a MONDO Disease when a MONDO mapping exists, otherwise to an
        HPO PhenotypicFeature. HPO and MONDO codings are used directly.

        Args:
            condition: The FHIR Condition resource to interpret.

        Returns:
            A Disease or PhenotypicFeature, or None if the condition has no coding or the
            code cannot be mapped.
        """
        codeable = condition.code
        if not codeable or not codeable.coding:
            return None

        coding = codeable.coding[0]
        system, code, display = coding.system, coding.code, coding.display or ""
        if not code:
            return None

        if system == SNOMED_SYSTEM:
            mondo = self.terminology_mapper.get_mondo_from_snomed(code)
            if mondo:
                return Disease(term=mondo)
            hpo = self.terminology_mapper.get_hpo_from_snomed(code)
            if hpo:
                return PhenotypicFeature(type=hpo)
        elif system == MONDO_SYSTEM:
            return Disease(term=OntologyClass(id=code, label=display))
        elif system == HPO_SYSTEM:
            return PhenotypicFeature(type=OntologyClass(id=code, label=display))

        return None
