# Third Party Packages
from pandera.typing import DataFrame
from loguru import logger
from sys import stderr

logger.remove()
logger.add(
    stderr,
    level="INFO",
    format="<cyan>[{file.name}:{line} - {function}()]</cyan> <green>{time:YYYY-MM-DD HH:mm:ss}</green> - {level} - <level>{message}</level>",
)

# Built-in Packages
import argparse
from typing import List

# My Custom Modules
import app.utils.files_processing as U
import app.src.adhoc.json_processing as A
import app.src.pandas_processing.load as L
import app.src.pandas_processing.clean as C
import app.src.pandas_processing.transform as T
from app.src.constants import (
    CLINICAL_TRIALS_PATHS,
    PUBMED_PATHS,
    DRUGS_PATHS,
    OUTPUT_PATH,
)


def clean_dataframes(
    clinical_df: DataFrame, pubmed_df: DataFrame, drugs_df: DataFrame
) -> List:
    # Standardize column names
    clinical_df = C.rename_column(clinical_df, {"scientific_title": "title"})
    drugs_df = C.rename_column(drugs_df, {"drug": "name"})
    logger.info("[Cleaning] - Successfully renamed columns.")

    # Standardize the Date format (into %Y-%m-%d)
    clinical_df = C.normalize_dates_format(clinical_df, "date", "%Y-%m-%d")
    pubmed_df = C.normalize_dates_format(pubmed_df, "date", "%Y-%m-%d")
    logger.info("[Cleaning] - Successfully standardized date formats.")

    # Merge duplicate rows together, filling in missing columns based on other rows
    clinical_articles_group = clinical_df.groupby(["title", "date"])
    clinical_df = clinical_articles_group.apply(T.merge_rows).reset_index(drop=True)

    pubmed_articles_group = pubmed_df.groupby(["title", "date"])
    pubmed_df = pubmed_articles_group.apply(T.merge_rows).reset_index(drop=True)
    logger.info("[Cleaning] - Successfully filled in missing data.")

    # Fill in missing IDs
    pubmed_df = C.fill_in_missing_ids_int(pubmed_df, "id")
    logger.info("[Cleaning] - Successfully interpolated missingIDs.")

    # Clean titles and names
    pubmed_df["title"] = pubmed_df["title"].apply(C.clean_titles)
    pubmed_df["journal"] = pubmed_df["journal"].apply(C.clean_titles)

    clinical_df["title"] = clinical_df["title"].apply(C.clean_titles)
    clinical_df["journal"] = clinical_df["journal"].apply(C.clean_titles)

    drugs_df["name"] = drugs_df["name"].apply(C.clean_titles)
    logger.info("[Cleaning] - Successfully cleaned all titles and names.")

    # Standardize the type of IDs used (string)
    pubmed_df = C.cast_id_as_string(pubmed_df, "id")
    clinical_df = C.cast_id_as_string(clinical_df, "id")

    return clinical_df, pubmed_df, drugs_df


def generate_graph_link(
    clinical_trials_path: List, pubmed_paths: List, drugs_paths: List, output_path: str
) -> None:
    # Load Data
    clinical_df = L.load_input_data(clinical_trials_path)
    pubmed_df = L.load_input_data(pubmed_paths)
    drugs_df = L.load_input_data(drugs_paths)

    # Clean dataframes
    clinical_df_cleaned, pubmed_df_cleaned, drugs_df_cleaned = clean_dataframes(
        clinical_df, pubmed_df, drugs_df
    )

    # Enrich the dataframes with the types of articles, before merging
    pubmed_df_cleaned["article_type"] = "PubMed"
    clinical_df_cleaned["article_type"] = "ClinicalTrial"

    # Merge the articles dataframes into one
    all_articles_df = T.merge_dataframes([pubmed_df_cleaned, clinical_df_cleaned])
    logger.info(
        "[Transform] - Successfully merged the pubmed and clinical trials dataframes."
    )

    # Remove empty strings
    all_articles_df_cleaned = C.drop_empty_titles_and_journals(all_articles_df)
    logger.info("[Cleaning] - Successfully droped rows with empty titles and names.")

    # Drop duplicate IDs and index dataframes
    drugs_df_cleaned, all_articles_df_cleaned = C.drop_duplicate_ids_then_index(
        drugs_df_cleaned, all_articles_df_cleaned
    )
    logger.info("[Cleaning] - Successfully droped rows with duplicate IDs.")

    # Finally, generate the graph as json file
    output_graph = T.build_link_graph_from_df(all_articles_df_cleaned, drugs_df_cleaned)
    U.write_dict_to_file(output_path, output_graph)
    logger.info(f"[Transform] - Link graph successfully written to {output_path}.")


def fetch_top_journals() -> List:
    """This function will return a list of the name(s) of the journal(s) that has mentioned most unique drugs."""
    graph_link_dict = U.import_json_file_as_dict(OUTPUT_PATH)

    unique_mentions_mapping = {}

    for journal_object in graph_link_dict["journals"]:
        curr_pubmed_articles, curr_clinical_trials_articles = (
            A.get_all_articles_from_journal(journal_object)
        )

        set_curr_mentioned_drugs = A.get_drugs_mentioned_by_journal(
            pubmed_of_journal=curr_pubmed_articles,
            clinical_trials_of_journal=curr_clinical_trials_articles,
            return_drug_names=False,  # Use IDs to be more accurate
        )

        unique_mentions_mapping[journal_object["title"]] = len(set_curr_mentioned_drugs)

    max_nb_unique_mentions = max(unique_mentions_mapping.values())
    top_journals = [
        key
        for key, value in unique_mentions_mapping.items()
        if value == max_nb_unique_mentions
    ]

    logger.info(
        f"The journal(s) {', '.join(top_journals)} has mentioned {max_nb_unique_mentions} unique drugs"
    )

    return top_journals


def fetch_drugs_mentioned_by_pubmed_journals(drug_name: str) -> List:
    """
    This function will, for a specific drugm return a list of all drugs mentioned by the same journals that are only referenced by pubmed articles.
    The list includes the input drug too
    """
    graph_link_dict = U.import_json_file_as_dict(OUTPUT_PATH)

    output_drug_mentions = A.get_drugs_mentioned_by_similar_journals(
        list_journals=graph_link_dict["journals"],
        drug_name=drug_name.title(),
        skip_clinical_trials=True,
    )

    return list(output_drug_mentions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hussein Ballouk - Test Data Engineering Servier"
    )

    parser.add_argument(
        "--pubmed_paths",
        type=str,
        help="String of `;` separated path(s) of the pubmed csv / json file(s). Default value : data/pubmed.csv;data/pubmed.json",
        default=PUBMED_PATHS,
    )

    parser.add_argument(
        "--clinical_trials_paths",
        type=str,
        help="String of `;` separated path(s) of the clinical trials csv / json file(s). Default value : data/clinical_trials.csv",
        default=CLINICAL_TRIALS_PATHS,
    )

    parser.add_argument(
        "--drugs_paths",
        type=str,
        help="String of `;` separated path(s) of the drug csv / json file(s). Default value : data/drugs.csv",
        default=DRUGS_PATHS,
    )

    parser.add_argument(
        "--output_path",
        type=str,
        help="The name and path of the output json file. Default value : output/graph_link.json",
        default=OUTPUT_PATH,
    )

    parser.add_argument(
        "--adhoc_drug_name",
        type=str,
        help="The name of the drug you wish to use in the adhoc question. Must use the get_drug_mentions action with this argument. Default value : None",
        default=None,
    )

    parser.add_argument(
        "action",
        type=str,
        choices=["generate_graph_link", "get_top_journal", "get_drug_mentions"],
        help="Manage the different parts of the application (allowed values: generate_graph_link, get_top_journal, get_drug_mentions). Please note that you must provide the --adhoc_drug_name if you waish to use the get_drug_mentions action",
    )

    args = parser.parse_args()

    if args.action == "generate_graph_link":
        generate_graph_link(
            clinical_trials_path=args.clinical_trials_paths.split(";"),
            pubmed_paths=args.pubmed_paths.split(";"),
            drugs_paths=args.drugs_paths.split(";"),
            output_path=args.output_path,
        )

    elif args.action == "get_top_journal":
        top_journals = fetch_top_journals()
        print(top_journals)

    elif args.action == "get_drug_mentions":
        if args.adhoc_drug_name is None:
            parser.error(
                "The get_drug_mentions action requires the use of --adhoc_drug_name flag."
            )
        else:
            output = fetch_drugs_mentioned_by_pubmed_journals(args.adhoc_drug_name)
            print(output)
