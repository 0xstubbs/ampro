import os
import json
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DRSUtils:
    def __init__(self):
        logger.info("Instantiating DRSUtils")

        self.drs_api_key = os.getenv("DRS_API_KEY")
        self.base_url = os.getenv("DRS_BASE_URL")
        self.date_format = "%y-%m-%dT%H:%M:%S.%fffZ"
        self.offset = 0
        self.has_more_items = True
        self.doc_type = "AD"
        self.list_of_docs = []
        self.paginate = True

    def _paginate_docs(self, docs_summary: dict) -> None:
        """
        This function checks if there are documents remaining to be collected.
        """
        offset = docs_summary["offset"]
        count = docs_summary["count"]

        docs_remaining = docs_summary["totalItems"] - (offset + count)

        if docs_summary["hasMoreItems"]:
            logger.info("There are {docs_remaining} documents remaining...")
            self.offset = docs_summary["offset"] + docs_summary["count"] + 1
        else:
            logger.info("There are no more docs to collect. Exiting...")
            # self.has_more_items = False
            self.paginate = False

    def _get_endpoint(self) -> str:
        if self.doc_type.lower() == "ad" or self.doc_type.lower() == "adfrawd":
            return "ADFRAWD"
        elif self.doc_type.lower() == "ac":
            return "AC"
        elif self.doc_type.lower() == "ead":
            return "ADFREAD"
        else:
            logger.error(f"Invalid document type: {self.doc_type}")
            raise ValueError(f"Invalid document type: {self.doc_type}")

    def _get_summary_from_response(self, response) -> dict:
        """
        This function takes a request response and returns the summary.
        """
        logger.info("Processing response to get summary")

        if not response.ok:
            logger.error(f"Response return with status code {response.status_code}")
            return {"Error": f"{response.status_code}"}
        try:
            summary = response.json().get("summary")
            if summary is None:
                raise ValueError("Response does not contain 'summary' key")
            return {"summary": summary}
        except json.JSONDecodeError:
            logger.error(f"JSON decoding failed for {response}")
            summary = {"Error": "Invalid JSON response"}
        except ValueError as e:
            logger.error(f"{e} in response: {response}")
            summary = {"Error": str(e)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            summary = {"Error": "Request error"}

        return summary

    def _get_documents_from_response(self, response):
        """
        This function takes a Response and extracts the documents into list.
        """
        logging.info("Processing Response to get documents.")
        if response.ok:
            documents = response.json().get("documents")
            self.list_of_docs.extend(documents)
        else:
            logging.error(f"Response Status Code: {response.status_code}")

    def _call_drs(self):
        logger.info(f"\n{'*'*50}\n_call_drs")

        endpoint = self._get_endpoint()
        headers = {
            "x-api-key": self.drs_api_key,
            "USER_AGENT": "curl/7.68.0",
        }
        payload = {
            "offset": self.offset,
            "docLastModifiedDate": self.doc_last_modified,
        }
        request_url = f"{self.base_url}{endpoint}"

        logger.info("Calling API...")
        response = requests.get(request_url, headers=headers, params=payload)
        logger.info(
            f"Response URL: {response.url}\nResponse Headers: {response.headers}\nResponse Status: {response.status_code}"
        )
        return response

    def get_docs(
        self,
        doc_type: str = "AD",
        offset: int = 0,
        paginate: bool = True,
        doc_last_modified: str = None,
    ) -> dict:
        """
        This function collects all documents of a specified type.
        See README.md for additional types.

        Params
        ------
        default                     Collects ADs, ACs, and EADs.
        AD | ad      ADFRAWD
        ad_nprm      ADNPRM         Airworthiness Directives: Notice of Proposed Rulemaking (NPRM)
        AC | ac      AC             Advisory Circulars
        EAD          ADFREAD        Emergency ADs

        """
        logger.info(
            f"****\nget_docs\n\nDocument: {doc_type}\nOffset: {offset}\n\nLast Modified Date Filter: {doc_last_modified}\nPaginate: {paginate}"
        )

        self.offset = offset
        self.doc_type = doc_type
        self.paginate = paginate
        self.doc_last_modified = doc_last_modified

        # logger.info(
        #     f"Calling `get_docs` with the following params: \ndoc_type: {self.doc_type}\noffset: {self.offset}"
        # )

        while True:
            self.paginate = paginate
            logger.info(f"\n\nPaginate: {self.paginate}\n\n")

            response = self._call_drs()

            if response.ok:
                summary = self._get_summary_from_response(response)
                self._get_documents_from_response(response)

                if not summary.get("hasMoreItems"):
                    self.paginate = False
                    logger.info(
                        "There are no more pages left. Setting pagination = False"
                    )
            else:
                logging.error(f"Response Status Code: {response.status_code}")
                self.paginate = False
                logging.info(f"Setting paginate to False...\nPaginate: {self.paginate}")


# This part only runs when drs_utils.py is executed directly
if __name__ == "__main__":
    # Testing code
    drs = DRSUtils()
    # Call some methods of DRSUtils for testing
    drs.get_docs("AD")
    help(drs.get_docs)
