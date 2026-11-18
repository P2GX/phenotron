# FHIR to Phenopackets Landscape Research

*Research date: 2026-03-19*

## Existing Tools and Libraries

### phenopacket-schema-fhir-interop (Java)

- **Repository**: https://github.com/phenopackets/phenopacket-schema-fhir-interop
- Official GA4GH interoperability library for bidirectional conversion between FHIR Bundles and Phenopackets
- Targets **FHIR DSTU3** and **Phenopacket Schema v1**
- Explicitly states: "The conversion is lossy as the focus of each standard is somewhat different"
- **Status**: Dormant since March 2021 (14 commits, 3 stars). Not updated for Phenopackets v2 or FHIR R4.

### hapi-pheno (Java)

- **Repository**: https://github.com/phenopackets/hapi-pheno
- FHIR client built on HAPI FHIR JPA server that has ingested the GA4GH Phenopacket IG
- Multi-module Maven project: `hapipheno-client` (Spring Boot), `hapipheno-core`, `whistle` (transformation utilities)
- Includes FHIR validation against the phenopacket extension (v0.1.0)
- **Status**: More active with 115 commits, last updated September 2025. GPL-3.0 licensed.

### c3g/phenopackets-to-fhir-converter (Python)

- **Repository**: https://github.com/c3g/phenopackets-to-fhir-converter
- **One-directional**: Phenopackets → FHIR only (not the reverse)
- Part of the CHORD Metadata service (Canadian genomics initiative)
- Implements mappings from the "Phenopackets on FHIR" IG
- Uses SMART on FHIR Python client for validation
- **Status**: ~16 commits, last updated ~2022. LGPL-3.0.

### BIH-CEI/rarelink (Python/HTML)

- **Repository**: https://github.com/BIH-CEI/rarelink
- REDCap-based framework that can export to both FHIR and Phenopackets independently from a common data model (RD-CDM)
- Does not convert directly between FHIR and Phenopackets; both are parallel export targets from the same intermediate representation
- Uses the toFHIR engine for FHIR output; has its own Phenopacket export engine
- Published in NPJ Genomics in Medicine (2025).
- **Status**: Active development.

### pnrobinson/hapi-pheno-server (Java)

- **Repository**: https://github.com/pnrobinson/hapi-pheno-server
- GA4GH Phenopacket FHIR IG utility server
- **Status**: Last updated September 2022.

### BIH-CEI/rd-cdm (Python)

- **Repository**: https://github.com/BIH-CEI/rd-cdm
- Ontology-based Rare Disease Common Data Model harmonizing ERDRI-CDS, FHIR v4.0.1, and Phenopacket Schema v2.0
- 78 data elements across 7 categories. Built on LinkML.
- Provides the conceptual mapping layer but not a runtime conversion tool.

## The FHIR Phenopacket Implementation Guide(s)

There are three generations of IG work:

### Generation 1: CSIRO "Phenopackets on FHIR" (ARCHIVED)

- By CSIRO (Australia's national science agency)
- Created FHIR profiles that directly mirror the Phenopacket schema structure
- Used FHIR **Composition** as the top-level container
- Mapped Individual → Patient, Disease → Condition (with extensions for coded onset/tumor staging), Biosample → Specimen (with many extensions)
- **Status**: Archived. This was the "top-down" approach.

### Generation 2: Official GA4GH IG

- **Repository**: phenopackets/phenopacket-schema-fhir-implementation-guide
- Built on the CSIRO work, drew from mCODE and Clinical Genomics Reporting IGs
- **Status**: 66 commits, last updated 2020. No official release.

### Generation 3: HL7 "Phenomics Exchange for Research and Diagnostics" (CURRENT)

- The active effort under **HL7 International / Clinical Interoperability Council**
- Version 1.0.0-ballot (December 2025)
- Accompanied by a Domain Analysis Document at https://phenopackets-analysis.readthedocs.io
- Key design statement: the IG is "meant to be conceptually equivalent but not directly interoperable" with the Phenopacket protobuf schema
- Currently defines only one profile: **Observation-Phenotype.fsh** (an Observation profile for phenotypic features)
- **Status**: Still in early development; the top-level container question (Composition vs Bundle) remains unresolved.

### Key Mappings from the Domain Analysis

| Phenopacket Element | FHIR Resource(s) | Notes |
|---|---|---|
| Phenopacket (container) | Composition or Bundle | Unresolved; Composition used historically, Bundle considered more appropriate |
| Individual (subject) | Patient (current IG), Person (proposed) | Person is role-neutral; Patient carries healthcare context |
| PhenotypicFeature | Observation | `.type` → `Observation.code`, `.severity`/`.modifier` → `Observation.component`, positive/negative → `Observation.valueBoolean` |
| Disease | Condition | Onset → `Condition.onset[x]`, staging → `Condition.stage` |
| Interpretation | DiagnosticReport | Maps to GenomicsReport profile (via Genomics Reporting IG) |
| Biosample | Specimen + references | Current IG uses Specimen with extensions; proposed approach distributes across multiple resources |

## Academic Literature

1. **Graefe et al. (2025)** — "Linking international registries to FHIR and Phenopackets with RareLink" — NPJ Genomics in Medicine (PMID: 41253795). Describes the RareLink framework.

2. **Graefe et al. (2025)** — "An ontology-based rare disease common data model harmonising international registries, FHIR, and Phenopackets" — Scientific Data (PMID: 39922817). The RD-CDM paper.

3. **Zhang, Cornet & Benis (2024)** — "Cross-Standard Health Data Harmonization using Semantics of Data Elements" — Scientific Data (PMID: 39702578). Harmonizes 5 standards (FHIR, OMOP, CDISC, Phenopackets, openEHR) across 64 data elements using semantic concept mapping (SSSOM/RDF).

4. **Cremonesi et al. (2023)** — "The need for multimodal health data modeling" — Journal of Biomedical Informatics (PMID: 37023843). Evaluates FHIR, OMOP, and Phenopackets for federated learning platforms.

5. **Rambla, Baudis et al. (2022)** — "Beacon v2 and Beacon networks" — Human Mutation (PMID: 35297548). Positions Beacon v2 alongside Phenopackets and FHIR for federated data discovery.

## Top-Down vs Bottom-Up Approaches

### Top-Down (Profile Mirroring)

- Used by the original CSIRO IG and the `phenopacket-schema-fhir-implementation-guide`
- Creates FHIR profiles that structurally mirror the Phenopacket schema
- Heavy use of FHIR extensions to capture Phenopacket-specific fields with no FHIR equivalent
- **Pros**: Near-lossless round-tripping, clear 1:1 correspondence
- **Cons**: The resulting FHIR resources look nothing like "normal" clinical FHIR data; essentially Phenopackets serialized as FHIR. Not useful for extracting phenotypic data from existing EHR endpoints. Requires hospitals to adopt the IG first.

### Bottom-Up (Extraction/Inference)

- Extracts phenotypic information from standard, unmodified FHIR resources as they exist in EHR systems
- Must infer Phenopacket semantics from clinical FHIR data that was never designed with Phenopackets in mind
- **Pros**: Works with real-world FHIR data; no need for systems to adopt a special IG
- **Cons**: Inherently lossy; many Phenopacket fields (e.g., `modifier`, `severity` on PhenotypicFeature) may not exist in standard FHIR; requires heuristics and terminology mapping
- **No existing tool performs robust bottom-up extraction.** This is a significant gap in the ecosystem.

### Middle Ground (HL7 Phenomics Exchange IG)

- Defines FHIR profiles that are conceptually equivalent to Phenopackets but use idiomatic FHIR patterns (e.g., `Observation.component` instead of extensions)
- Explicitly states it is "conceptually equivalent but not directly interoperable"
- Still in early ballot with minimal profile coverage

## FHIR Resources as Phenotypic Data Sources

| FHIR Resource | Phenopacket Target | Priority |
|---|---|---|
| **Patient** | Individual (demographics, sex, DOB) | Primary |
| **Condition** | Disease, PhenotypicFeature (diagnosis, onset, staging) | Primary |
| **Observation** | PhenotypicFeature, Measurement (labs, vitals, clinical findings) | Primary |
| **MedicationStatement / MedicationRequest** | MedicalAction (Treatment) | Secondary |
| **Procedure** | MedicalAction (Procedure) | Secondary |
| **Specimen** | Biosample | Secondary |
| **DiagnosticReport** | Interpretation (especially genomics reporting) | Secondary |
| **FamilyMemberHistory** | Family/Pedigree | Tertiary |
| **DocumentReference** | File (linking VCF/sequencing data) | Tertiary |
| **Encounter** | Temporality context (no direct Phenopacket equivalent) | Supporting |

## Key Findings

1. **No production-quality FHIR R4 → Phenopackets v2 converter exists** in any language.
2. The official interop library (`phenopacket-schema-fhir-interop`) is stuck on FHIR DSTU3 and Phenopackets v1.
3. The HL7 Phenomics Exchange IG is still in ballot with only one profile defined.
4. **Bottom-up extraction from real clinical FHIR data is essentially unexplored** in existing tools — all current approaches assume either Phenopacket-profiled FHIR data or a common intermediate model.
5. The conversion is acknowledged as inherently lossy in both directions due to fundamentally different design goals (clinical care vs. genomic/phenotypic research).
6. The core trio for bottom-up extraction is **Patient + Condition + Observation**. MedicationStatement/Request and Procedure become important when populating the `medical_actions` field of Phenopackets v2.
7. The terminology mapping layer (SNOMED → HPO/MONDO) is the critical component that makes bottom-up extraction feasible.
