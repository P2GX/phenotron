# phenotron

![Build status](https://img.shields.io/github/actions/workflow/status/TheJacksonLaboratory/phenotron/test.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/phenotron)

A Python library and CLI that connects to a FHIR server via SMART on FHIR and transforms
clinical data into [GA4GH Phenopackets](https://phenopacket-schema.readthedocs.io/) (v2).

> **Status: alpha.** The pipeline works end-to-end for Patient and Condition resources, but
> terminology mapping is a small built-in stub and APIs may change.

## What it does

```
FHIR server ──SMART on FHIR──▶ Patient + Conditions ──phenotron──▶ Phenopacket (JSON)
```

| FHIR (R4)                       | Phenopacket                                   |
|---------------------------------|-----------------------------------------------|
| `Patient.id`                    | `subject.id`                                  |
| `Patient.gender`                | `subject.sex`                                 |
| `Patient.birthDate`             | `subject.dateOfBirth`                         |
| `Patient.deceasedBoolean`       | `subject.vitalStatus`                         |
| —                               | `subject.taxonomy` = `NCBITaxon:9606`         |
| `Condition` (SNOMED CT → MONDO) | `diseases[]`                                  |
| `Condition` (SNOMED CT → HPO)   | `phenotypicFeatures[]`                        |
| `Condition` (HPO / MONDO coded) | `phenotypicFeatures[]` / `diseases[]` directly |

When a SNOMED CT code maps to both MONDO and HPO, the MONDO disease is used.

## Quickstart

Requires Python 3.11+ and [Poetry](https://python-poetry.org/).

```shell
git clone https://github.com/TheJacksonLaboratory/phenotron.git
cd phenotron
poetry install
```

Run against the public HAPI FHIR R4 test server (the default when no `--settings` is given):

```shell
poetry run phenotron transform --patient-id <PATIENT_ID>
```

The Phenopacket is printed as JSON to stdout; logs go to stderr. Example output:

```json
{
  "id": "alex-chen",
  "subject": {
    "id": "alex-chen",
    "dateOfBirth": "1982-03-15T00:00:00Z",
    "vitalStatus": { "status": "ALIVE" },
    "sex": "MALE",
    "taxonomy": { "id": "NCBITaxon:9606", "label": "Homo sapiens" }
  },
  "diseases": [
    { "term": { "id": "MONDO:0005148", "label": "type 2 diabetes mellitus" } }
  ]
}
```

Data on the public HAPI server changes often, so a given patient ID may disappear.

### Connecting to your own FHIR server

Pass a SMART app settings file:

```shell
poetry run phenotron transform --patient-id <PATIENT_ID> --settings smart.json
```

```json
{
  "app_id": "phenotron",
  "api_base": "https://your-fhir-server/baseR4",
  "redirect_uri": "http://localhost:8000/fhir-app/",
  "scope": "user/*.*"
}
```

If the server requires authorization, phenotron opens the authorization URL in your browser
and prompts for the returned code.

## Library usage

```python
from fhirclient.models.patient import Patient
from fhirclient.models.condition import Condition
from phenotron.fhir import FhirConverter, TerminologyMapper

fc = FhirConverter(TerminologyMapper())
individual = fc.convert_patient(patient)          # -> phenopackets Individual
features = fc.convert_conditions(conditions)      # -> list of Disease / PhenotypicFeature / None
```

## Development

```shell
poetry install
poetry run pytest
```

## Current limitations

- Terminology mapping is a hard-coded stub covering a handful of SNOMED CT codes
  (`phenotron/fhir/terminology.py`); unmapped conditions are dropped.
- Only the first coding of each Condition is considered.
- Observations are not yet mapped into the Phenopacket.
- `metaData` (resources, created-by) is not yet populated, so output is not yet a fully
  valid Phenopacket.
- The `phenotron` 0.1.0 release on PyPI predates this work; install from source for now.

## Further reading

- [Executive summary & roadmap](docs/EXECUTIVE_SUMMARY.md)
- [FHIR → Phenopackets landscape research](docs/research/fhir_to_phenopackets_landscape.md)

## License

MIT
