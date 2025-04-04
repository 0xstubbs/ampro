from datetime import datetime
import polars as pl
import time
import os
import json
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set the DRS_API_KEY as a variable that in the module rather than putting it in the class since it doesn't ever change.

DRS_API_KEY = os.getenv("DRS_API_KEY")
if DRS_API_KEY is None:
    logger.error("No DRS_API_KEY found in .env file. Please input DRS_API_KEY.")
    DRS_API_KEY = input("Enter DRS_API_KEY: ")
else:
    logger.info("DRS_API_KEY found and loaded successfully.")

# Set the BASE_URL from the .env or .config file.

# BASE_URL = os.getenv("DRS_BASE_URL")
BASE_URL = "https://drs.faa.gov/api/drs/data-pull/"
if BASE_URL is None:
    logger.error(
        "DRS_BASE_URL not found in environment variable. Make sure you have a .env file."
    )
    BASE_URL = input("Enter the BASE_URL: ")
else:
    logger.info("BASE_URL found and loaded successfully.")

# Set any other variables as necessary
DATE_FORMAT = "%y-%m-%dT%H:%M:%S.%fffZ"


class drs_utils:
    def __init__(self):
        logger.info("Instantiating drs_utils")
        self.session = requests.Session()
        self.offset = 0
        self.has_more_items = True
        self.record = "AD"
        self.list_of_records = []
        self.paginate = True
        self.records = {}
        self.summary = {}

    def _paginate_records(self, response_summary: dict) -> None:
        """
        This function checks if there are documents remaining to be collected.
        """

        if response_summary["hasMoreItems"]:
            logger.info(
                f"There are {response_summary['totalItems']} documents remaining..."
            )
            self.offset = response_summary["offset"] + response_summary["count"] + 1
        else:
            logger.info("There are no more records to collect. Exiting...")
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

        # Normalize the record_type to correct for upper or lowercase entries
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

    def _get_summary_from_response(self, response) -> None:
        """
        This function takes a request response and returns the summary.
        """
        logger.info("Processing response to get summary")

        if not response.ok:
            logger.error(f"Response return with status code {response.status_code}")
            self.summary = {"Error": f"{response.status_code}"}
        try:
            summary = response.json().get("summary")
            if summary is None:
                raise ValueError("Response does not contain 'summary' key")
            else:
                self.summary = summary
        except json.JSONDecodeError:
            logger.error(f"JSON decoding failed for {response}")
            self.summary = {"Error": "Invalid JSON response"}
        except ValueError as e:
            logger.error(f"{e} in response: {response}")
            self.summary = {"Error": str(e)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            self.summary = {"Error": "Request error"}

        # return summary

    def _get_records_from_response(self, response):
        """
        This function takes a Response and extracts the documents into list.
        """
        logging.info("Processing Response to get records.")
        if response.ok:
            records = response.json().get("documents")
            self.list_of_records.extend(records)
            logger.info(f"# of Documents: {len(self.list_of_records)}")
            self.records = records
        else:
            logging.error(f"Response Status Code: {response.status_code}")

    def _call_drs(self):
        logger.info(f"\n{'*' * 50}\n_call_drs")

        endpoint = self._get_endpoint()

        headers = {
            "x-api-key": DRS_API_KEY,
            "USER_AGENT": "curl/7.68.0",
        }
        if self.doc_last_modified == "":
            payload = {"offset": self.offset}
        else:
            payload = {
                "offset": self.offset,
                "docLastModifiedDate": self.doc_last_modified,
            }
        request_url = f"{BASE_URL}{endpoint}"

        logger.info("Calling API...")
        response = requests.get(request_url, headers=headers, params=payload)

        logger.info(
            f"Response URL: {response.url} Response Status: {response.status_code}"
        )
        return response

    def _save_to_parquet(self, response, loop_number):
        """
        This function saves raw responses to parquet for easier processing later
        """
        print(len(response))
        columns_to_select = [
            "drs:documentNumber",
            "drs:status",
            "drs:adfrawdMake",
            "drs:adfrawdModel",
            "drs:adfrawdProductType",
            "drs:adfrawdProductSubType",
            "drs:adfrawdSubject",
            "drs:adfrawdAffectedAD",
            "drs:adfrawdSupersededAD",
            "drs:title",
            "drs:adfrawdAction",
            "drs:adfrawdSummary",
            "drs:adfrawdSupplementaryInfo",
            "drs:adfrawdRegulatoryText",
            "drs:adfrawdIssueDate",
            "drs:effectiveDate",
            "documentURL",
            "mainDocumentDownloadURL",
            "mainDocumentFileName",
            "hasMoreAttachments",
        ]
        lf_schema = {
            "doc_number": pl.String,
            "status": pl.String,
            "make": pl.List(pl.String),
            "model": pl.List(pl.String),
            "product_type": pl.List(pl.String),
            "product_subtype": pl.List(pl.String),
            "subject": pl.String,
            "affected_ad": pl.List(pl.String),
            "superseded_ad": pl.List(pl.String),
            "title": pl.String,
            "action": pl.String,
            "summary": pl.String,
            "supplementary_info": pl.String,
            "regulatory_text": pl.String,
            "issue_date": pl.String,
            "effective_date": pl.String,
            "doc_url": pl.String,
            "doc_download_url": pl.String,
            "doc_filename": pl.String,
            "has_more_attachments": pl.Boolean,
        }
        df = (
            pl.from_dicts(
                response, infer_schema_length=10000
            )  # , schema=lf_schema, infer_schema_length=100000)
            .select(columns_to_select)
            .rename(
                {
                    "drs:documentNumber": "doc_number",
                    "drs:status": "status",
                    "drs:adfrawdMake": "make",
                    "drs:adfrawdModel": "model",
                    "drs:adfrawdProductType": "product_type",
                    "drs:adfrawdProductSubType": "product_subtype",
                    "drs:adfrawdSubject": "subject",
                    "drs:adfrawdAffectedAD": "affected_ad",
                    "drs:adfrawdSupersededAD": "superseded_ad",
                    "drs:title": "title",
                    "drs:adfrawdAction": "action",
                    "drs:adfrawdSummary": "summary",
                    "drs:adfrawdSupplementaryInfo": "supplementary_info",
                    "drs:adfrawdRegulatoryText": "regulatory_text",
                    "drs:adfrawdIssueDate": "issue_date",
                    "drs:effectiveDate": "effective_date",
                    "documentURL": "doc_url",
                    "mainDocumentDownloadURL": "doc_download_url",
                    "mainDocumentFileName": "doc_filename",
                    "hasMoreAttachments": "has_more_attachments",
                }
            )
            .with_columns(
                [
                    pl.col("affected_ad").cast(pl.List(pl.Utf8)),
                    pl.col("superseded_ad").cast(pl.List(pl.Utf8)),
                    pl.col("issue_date").cast(pl.Utf8),
                    pl.col("summary").cast(pl.Utf8),
                    pl.col("supplementary_info").cast(pl.Utf8),
                ]
            )
        )

        output_file = f"./tmp_data/{datetime.now().strftime('%Y%m%d')}_{loop_number}_{self.doc_type}_raw_data.parquet"

        df.write_parquet(output_file)

    def get_records(
        self,
        doc_type: str = "ad",
        offset: int = 0,
        paginate: bool = True,
        doc_last_modified: str = "",
    ):
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
            f"****\nget_records\n\nDocument: {doc_type}\nOffset: {offset}\n\nLast Modified Date Filter: {doc_last_modified}\nPaginate: {paginate}"
        )

        self.offset = offset
        self.doc_type = doc_type
        self.paginate = paginate
        self.doc_last_modified = doc_last_modified
        logger.info(
            f"\n{'*' * 50}\nget_records\nDocument Type: {doc_type}\nOffset: {offset}\nPaginate: {paginate}"
        )
        logger.info("Entering pagination loop...")
        i = 0
        increment = 750

        while self.paginate is True:
            logger.info(f"Pagination Loop #{i}")
            self.paginate = paginate
            try:
                response = self._call_drs()
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Request failed for {self.doc_type} with {offset} with error: {e}"
                )
                raise
            if response.ok:
                logger.info("Respoonse received...")
                self._get_summary_from_response(response)
                logger.info("Summary from response...")
                self._get_records_from_response(response)
                logger.info("Records from response...")
                data = self.records

                self._save_to_parquet(data, i)
                # with open(
                #     f"{datetime.now().strftime('%Y%m%d')}_{self.doc_type}_raw_data.json",
                #     "a",
                # ) as f:
                #     f.write(json.dumps(data) + "\n")
                # # return data
                #
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


# This part only runs when drs_utils.py is executed directly
if __name__ == "__main__":
    logger.info("Calling __main__")
    start_time = time.time()
    # Testing code
    drs = drs_utils()
    # Call some methods of DRSUtils for testing
    drs.get_records("ad")
    end_time = time.time()

    total_time = end_time - start_time

    print(f"Total Run Time: {total_time} seconds")
#    help(drs.get_records)
