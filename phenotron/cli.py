import click
import logging
import webbrowser
import json
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.condition import Condition
from .fhir import FhirConverter, TerminologyMapper
from phenopackets import Phenopacket, PhenotypicFeature, Disease
from google.protobuf.json_format import MessageToJson

@click.group()
def cli():
    pass

@cli.command(name='transform')
@click.option('--settings', type=click.Path(exists=True), help='Path to SMART app settings JSON.')
@click.option('--patient-id', required=True, help='FHIR Patient resource ID.')
def transform(settings, patient_id):
    """
    Transforms a FHIR Patient resource into a Phenopacket using SMART on FHIR.

    Without --settings, connects to the public HAPI FHIR R4 test server.

    Fetches the Patient and their Conditions, maps them to a Phenopacket, and prints
    the Phenopacket as JSON to stdout.
    """
    setup_logging()
    if settings:
        with open(settings) as f:
            smart_settings = json.load(f)
    else:
        smart_settings = {
            "app_id": "phenotron",
            "api_base": "https://hapi.fhir.org/baseR4",
            "redirect_uri": "http://localhost:8000/fhir-app/",
            "scope": "user/*.*"
        }
    smart = client.FHIRClient(settings=smart_settings)
    if not smart.ready:
        smart.prepare()
        logging.info("SMART client prepared successfully.")
        if not smart.ready:
            if not smart.authorize_url:
                click.echo("Authorization URL is not available.")
                exit(1)
            click.echo(f"Open this URL in your browser to authorize:\n{smart.authorize_url}")
            webbrowser.open(smart.authorize_url)
            code = click.prompt("Paste the authorization code here")
            smart.handle_callback(code)
    else: 
        logging.info("SMART client prepared successfully.")
    fc = FhirConverter(TerminologyMapper())
    logging.info(f"Fetching Patient - {patient_id}")
    individual =  fc.convert_patient(Patient.read(patient_id, smart.server))
    logging.info(f"Mapped Individual - {individual.id}")
    
    search = Condition.where(struct={'patient': f'Patient/{patient_id}'})
    conditions = search.perform_resources(smart.server)
    features = fc.convert_conditions(
        [Condition(r.as_json()) for r in conditions]
    )
    phenotypes = [f for f in features if isinstance(f, PhenotypicFeature)]
    diseases = [f for f in features if isinstance(f, Disease)]
    logging.info(f"Found {len(phenotypes)} phenotypic features and {len(diseases)} diseases.")
    phenopacket = Phenopacket(
        id=individual.id, subject=individual, phenotypic_features=phenotypes, diseases=diseases
    )
    click.echo(MessageToJson(phenopacket))

def setup_logging():
    level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s %(name)-20s %(levelname)-3s : %(message)s"
    )
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

if __name__ == "__main__":
    cli()
