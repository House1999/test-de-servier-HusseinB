import os

CLINICAL_TRIALS_PATHS = os.environ["ClinicalTrialsPaths"].split(";")
PUBMED_PATHS = os.environ["PubMedPaths"].split(";")
DRUGS_PATHS = os.environ["DrugsPaths"].split(";")
OUTPUT_PATH = os.environ["OutputPath"]
