from .terminology import TerminologyMapper
from phenopackets import PhenotypicFeature
from typing import Dict, Any, Optional


class ObservationInterpreter:
    """
    Interprets quantitative FHIR Observations to create qualitative PhenotypicFeatures.
    """

    def __init__(self, terminology_mapper: TerminologyMapper):
        self.terminology_mapper = terminology_mapper

    def interpret_observation(self, obs_resource: Dict[str, Any]) -> Optional[PhenotypicFeature]:
        """
        Applies clinical logic to an Observation resource.

        Example logic: If systolic blood pressure > 140, create a "Hypertension" phenotype.
        """
        code = obs_resource.get("code", {}).get("coding", [{}])[0].get("code")
        value_quantity = obs_resource.get("valueQuantity", {})
        value = value_quantity.get("value")
        unit = value_quantity.get("unit")

        # Rule for Systolic Blood Pressure (LOINC: 8480-6)
        if code == "8480-6" and unit == "mm[Hg]" and value and value > 140:
            hpo_term = self.terminology_mapper.get_hpo_from_loinc(code)
            if hpo_term:
                return PhenotypicFeature(type=hpo_term)

        # Add more rules here for other observations...

        return None
    
    

