# Third-party packages
from pandera.typing import DataFrame
from loguru import logger
from sys import stderr

logger.remove()
logger.add(
    stderr,
    level="INFO",
    format="<cyan>[{file.name}:{line} - {function}()]</cyan> <green>{time:YYYY-MM-DD HH:mm:ss}</green> - {level} - <level>{message}</level>",
)


# Built-in packages
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class JournalMentions:
    title: str
    drugs_dataFrame: DataFrame
    journal_articles_dataFrame: DataFrame  # Articles of the current journal only
    pubmed_publications: List = field(default_factory=list, init=False)
    clinical_trials_publications: List = field(default_factory=list, init=False)

    def extract_drug_from_publication_title(self, article_title: str) -> List:
        """
        Find the name(s) of the drug(s) mentioned in the any given article title.

        Parameters:
            - article_title (str): The title of the article to analyze.

        Returns:
            - List: A list of mentioned drugs in the format [drug_id, drug_name].
        """
        title_words_set = set(article_title.split())

        mentioned_drugs = []

        for drug_id, row in self.drugs_dataFrame.iterrows():
            if row["name"] in title_words_set:
                mentioned_drugs.append([drug_id, row["name"]])

        if mentioned_drugs == []:
            # No drug found, and given our hypothesis, we skip it
            logger.warning(
                f"No drug was mentioned in the following title : `{article_title}`"
            )

        return mentioned_drugs

    def get_article_information_from_id(self, article_id: str) -> Dict:
        """
        Get all information about an article based on the provided article ID.

        Parameters:
            - article_id (str): The unique identifier of the article.

        Returns:
            - article_info: A dictionary containing information about the article like the title, mention date, and type of the article.
        """
        current_article_row = self.journal_articles_dataFrame.loc[article_id]

        article_title = current_article_row["title"]
        mention_date = current_article_row["date"]
        article_type = current_article_row["article_type"]

        # Transform date to string
        mention_date_str = datetime.strftime(mention_date, "%Y-%m-%d")

        article_info = {
            "title": article_title,
            "date": mention_date_str,
            "isPubMed": True if article_type == "PubMed" else False,
            "isClinical": True if article_type == "ClinicalTrial" else False,
        }

        return article_info

    def build_links_articles_drug_mentions(self) -> None:
        """
        Builds, for a each journal, links between each articles referencing the journal and the drug mentioned in the title.

        It builds a dictionary describing the link between each article and the drug mentioned. Dictionary format :
            - articleId: ID of the article.
            - articleTitle: Title of the article.
            - mentionDate: The date of the article publication / drug mention.
            - mentionedDrugID: ID of the drug mentioned in the title of the article.
            - mentionedDrugName: Name of the drug mentioned in the title of the article.

        Raises an exception if an article is neither clinical nor from PubMed.
        """
        for article_id in self.journal_articles_dataFrame.index:
            # Get info about articles
            article_info = self.get_article_information_from_id(article_id)

            # Find mentioned drug(s)
            list_mentioned_drugs = self.extract_drug_from_publication_title(
                article_info["title"]
            )

            for mentioned_drug_info in list_mentioned_drugs:
                mentioned_drug_id, mentioned_drug_name = mentioned_drug_info

                currLinkDict = {
                    "articleId": article_id,
                    "articleTitle": article_info["title"],
                    "mentionDate": article_info["date"],
                    "mentionedDrugID": mentioned_drug_id,
                    "mentionedDrugName": mentioned_drug_name,
                }

                if article_info["isPubMed"] is True:
                    self.pubmed_publications.append(currLinkDict)
                elif article_info["isClinical"] is True:
                    self.clinical_trials_publications.append(currLinkDict)
                else:
                    raise Exception(
                        f"Something went wrong, the article { article_info['title']} is neither clinical nor pubmed"
                    )

    def generate_article_link_graph_dict(self) -> Dict:
        """
        This function will return a dictionary representing the complete link graph. It contains all entities and relations.
        It Executes the method above to build links between each article and mentioned drug, then shapes up the output file.

        Returns:
            - output : Dictionary representing the complete link graph with all entities and relations.
        """
        self.build_links_articles_drug_mentions()

        output = {
            "title": self.title,
            "referencedBy": {
                "pubmedArticles": self.pubmed_publications,
                "clinicalTrials": self.clinical_trials_publications,
            },
        }

        return output
