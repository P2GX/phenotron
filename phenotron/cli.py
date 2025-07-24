import click
import logging
import webbrowser
import json
from fhirclient import client
from fhirclient.models.patient import Patient
from .fhir import FhirConverter, TerminologyMapper
from phenopackets import Phenopacket

@click.group()
def cli():
    pass

@cli.command(name='transform')
@click.option('--settings', type=click.Path(exists=True), help='Path to SMART app settings JSON.')
@click.option('--patient-id', required=True, help='FHIR Patient resource ID.')
def transform(settings, patient_id):
    """
    Transforms a FHIR Patient resource into a Phenopacket using SMART on FHIR.

    Args:
        settings (str): Path to SMART app settings JSON file. If not provided, default settings are used.
        patient_id (str): FHIR Patient resource ID to fetch and convert.

    This command fetches a FHIR Patient resource using the provided settings and patient ID,
    converts it to a Phenopacket, and outputs the subject's date of birth.
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
    phenopacket: Phenopacket = fc.convert_patient(Patient.read(patient_id, smart.server))
    logging.info(phenopacket)
    pass

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
