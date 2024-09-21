# Third Party Packages
from loguru import logger
from sys import stderr

logger.remove()
logger.add(
    stderr,
    level="INFO",
    format="<cyan>[{file.name}:{line} - {function}()]</cyan> <green>{time:YYYY-MM-DD HH:mm:ss}</green> - {level} - <level>{message}</level>",
)

# Built-in Packages
from datetime import datetime
import argparse

# My Custom Modules
from src.constants import CLINICAL_TRIALS_PATHS, PUBMED_PATHS, DRUGS_PATHS, OUTPUT_PATH


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hussein Ballouk - Test Data Engineering Servier"
    )

    parser.add_argument(
        "--row_config_id",
        type=str,
        help="The custom export file unique_id which represents the DAG's objective.",
    )
    parser.add_argument("--supplier_entity", type=str, help="The supplier entity name.")

    parser.add_argument(
        "--expiration_days",
        type=str,
        default="",
        help="The expiration time to be applied to the views and tables.",
    )
    parser.add_argument(
        "--dag_timestamp", type=str, default="", help="The DAG run's timestamp."
    )

    parser.add_argument(
        "--supplier_holding", type=str, default="", help="The supplier holding name."
    )

    parser.add_argument(
        "--correlation_id",
        type=str,
        default="",
        help="This is used to refer to the monitoring row.",
    )

    parser.add_argument(
        "--monitoring_table_id",
        type=str,
        default="",
        help="This the full id of the monitoring table (PROJECT.DATASET.TABLE).",
    )

    parser.add_argument(
        "--scope",
        type=str,
        help="The name of the project you are trying to export from",
    )

    parser.add_argument(
        "action",
        type=str,
        choices=[
            "export_contract_file",
            "get_sql_query",
            "materialize_table",
            "export_files_gcs",
            "expose_view_gah",
        ],
        help="Manage the different parts of the application (allowed values: export_contract_file, get_sql_query, materialize_table, export_files_gcs, expose_view_gah)",
    )

    args = parser.parse_args()
