from datetime import datetime
import time
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
        if self.drs_api_key is None:
            logger.error(
                "API key was not found in environment variables. Please input DRS API key."
            )
            self.drs_api_key = input("Enter DRS API Key: ")
            print("DRS API Key: {self.drs_api_key}")
        else:
            logger.info(
                "DRS Key found in environment variable and loaded successfully."
            )

        self.base_url = os.getenv("DRS_BASE_URL")
        if self.base_url is None:
            logger.error(
                "DRS_BASE_URL not found in environment variable. Make sure you have a .env file."
            )
        self.date_format = "%y-%m-%dT%H:%M:%S.%fffZ"
        self.offset = 0
        self.has_more_items = True
        self.doc_type = "AD"
        self.list_of_docs = []
        self.paginate = True
        self.documents = dict
        self.summary = dict

    def _paginate_docs(self, docs_summary: dict) -> None:
        """
        This function checks if there are documents remaining to be collected.
        """

        if docs_summary["hasMoreItems"]:
            logger.info("There are {docs_remaining} documents remaining...")
            self.offset = docs_summary["offset"] + docs_summary["count"] + 1
        else:
            logger.info("There are no more docs to collect. Exiting...")
            self.paginate = False

    def _get_endpoint(self) -> str:
        endpoint_mapping = {
            # Airworthiness Directives Mapping
            "ad": "ADFRAWD",
            "adfrawd": "ADFRAWD",
            "ads": "ADFRAWD",
            "airworthiness directives": "ADFRAWD",
            "airworthiness directive": "ADFRAWD",
            # Advisory Circular Mappings
            "ac": "AC",
            "advisory circular": "AC",
            "acs": "AC",
            "advisory circulars": "AC",
            "ead": "ADFREAD",
        }

        # Normalize the doc_type to correct for upper or lowercase entries
        normalized_doc_type = self.doc_type.lower()

        # Try to get the mapping if invalid enpoint was entered prompt the user to input a new endpoint and give them valid options
        endpoint = endpoint_mapping.get(normalized_doc_type)
        if endpoint is None:
            print(
                f"{normalized_doc_type} is not a valid document. Please use one of the following:\n\tAD\tAirworthiness Directives\n\tAC\tAdvisory Circular"
            )
            endpoint = endpoint_mapping.get(input('Enter "AD" or "AC": ').lower(), "ad")
            self.doc_type = endpoint
            logger.info(
                f"Endpoint corrected to: {endpoint}self.doc_type updated to: {self.doc_type}"
            )
            logger.info(f"self.doc_type updated to: {self.doc_type}")
        else:
            logger.info(f"Endpoint is: {endpoint}")

        return endpoint

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
            else:
                self.summary = summary
        except json.JSONDecodeError:
            logger.error(f"JSON decoding failed for {response}")
            summary = {"Error": "Invalid JSON response"}
        except ValueError as e:
            logger.error(f"{e} in response: {response}")
            summary = {"Error": str(e)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            summary = {"Error": "Request error"}

        # return summary

    def _get_documents_from_response(self, response):
        """
        This function takes a Response and extracts the documents into list.
        """
        logging.info("Processing Response to get documents.")
        if response.ok:
            documents = response.json().get("documents")
            self.list_of_docs.extend(documents)
            logger.info(f"# of Documents: {len(self.list_of_docs)}")
            self.documents = documents
            return documents
        else:
            logging.error(f"Response Status Code: {response.status_code}")

    def _call_drs(self):
        logger.info(f"\n{'*'*50}\n_call_drs")

        endpoint = self._get_endpoint()

        headers = {
            "x-api-key": self.drs_api_key,
            "USER_AGENT": "curl/7.68.0",
        }
        if self.doc_last_modified == "":
            payload = {"offset": self.offset}
        else:
            payload = {
                "offset": self.offset,
                "docLastModifiedDate": self.doc_last_modified,
            }
        request_url = f"{self.base_url}{endpoint}"

        logger.info("Calling API...")
        response = requests.get(request_url, headers=headers, params=payload)
        logger.info(
            f"Response URL: {response.url}\nResponse Status: {response.status_code}"
        )
        return response

    def get_docs(
        self,
        doc_type: str = "AD",
        offset: int = 0,
        paginate: bool = True,
        doc_last_modified: str = "",
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
        # logger.info(f"\n{'*'*50}\nget_docs\nDocument Type: {doc_type}\nOffset: {offset}\nPaginate: {paginate}")

        self.offset = offset
        self.doc_type = doc_type
        self.paginate = paginate
        self.doc_last_modified = doc_last_modified

        # logger.info(
        #     f"Calling `get_docs` with the following params: \ndoc_type: {self.doc_type}\noffset: {self.offset}"
        # )

        logger.info(
            f"\n{'*'*50}\nget_docs\nDocument Type: {doc_type}\nOffset: {offset}\nPaginate: {paginate}"
        )
        logger.info("Entering pagination loop...")
        i = 0
        increment = 750

        while self.paginate is True:
            logger.info(f"Pagination Loop #{i}")
            self.paginate = paginate

            response = self._call_drs()

            if response.ok:
                self._get_summary_from_response(response)
                self._get_documents_from_response(response)
                logger.info(f"Documents: {self.documents[0]['drs:documentNumber']}")

                logger.info(f"{self.summary['hasMoreItems']}")
                if not self.summary["hasMoreItems"]:
                    self.paginate = False
                    logger.info(
                        "There are no more pages left. Setting pagination = False"
                    )
                else:
                    self.offset = self.offset + increment
                    logger.info(f"New offset: {self.offset}")

                    i += 1
            else:
                logging.error(f"Response Status Code: {response.status_code}")
                self.paginate = False
                logging.info(f"Setting paginate to False...\nPaginate: {self.paginate}")

        logger.info("Saving ADs to a JSON file for future processing...")
        with open(
            f"{datetime.now().strftime('%Y%m%d')}_{self.doc_type}_raw_data.json", "w"
        ) as f:
            for doc in self.list_of_docs:
                json_string = json.dumps(
                    doc, indent=4, separators=(",", ":"), sort_keys=True
                )
                f.write(json_string + "\n")


# This part only runs when drs_utils.py is executed directly
if __name__ == "__main__":
    logger.info("Calling __main__")
    start_time = time.time()
    # Testing code
    drs = DRSUtils()
    # Call some methods of DRSUtils for testing
    drs.get_docs("AD")
    end_time = time.time()

    total_time = end_time - start_time

    print(f"Total Run Time: {total_time} seconds")
#    help(drs.get_docs)
