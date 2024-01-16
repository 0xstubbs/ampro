import os
import requests
import logging
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
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

    def paginate_docs(self, docs_summary: dict) -> None:
        """
        This function checks if there are documents remaining to be collected.
        """
        offset = docs_summary['offset']
        count = docs_summary['count']

        docs_remaining = docs_summary['totalItems'] - (offset + count)

        if docs_summary['hasMoreItems']:
            logger.info("There are {docs_remaining} documents remaining...")
            self.offset=docs_summary['offset'] + docs_summary['count'] + 1
        else:
            logger.info("There are no more docs to collect. Exiting...")
            self.has_more_items = False

    def get_docs(
        self, doc_type: str = "AD", offset: int = 0, doc_last_modified: str = None
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
        self.offset = offset
        self.doc_type = doc_type

        logger.info(f"Calling `get_docs` with the following params: \ndoc_type: {self.doc_type}\noffset: {self.offset}")

        while self.has_more_items:
            logger.info(f"Paginating - Offset: {self.offset}")
            
            if self.doc_type.lower() == "ad" or self.doc_type.lower() == "adfrawd":
                request_url = f"{self.base_url}ADFRAWD"
            elif doc_type.lower() == "ac":
                request_url = f"{self.base_url}AC"
            elif doc_type.lower() == "ead":
                request_url = f"{self.base_url}ADFREAD"

            headers = {"x-api-key": self.drs_api_key}

            payload = {
                "offset":self.offset
                # docLastModifiedDate = strptime(doc_last_modified, date_format)
            }
            logger.info(f"Sending request with the following:\nRequest URL: {request_url}\nHeaders: {headers}\nParams: {payload}")

            try:
                logger.info("Sending request...")
                r = requests.get(
                    request_url,
                    headers=headers,
                    params=payload
                )
            except Exception:
                logging.exception("Exception occurred")

            if not r.raise_for_status():
                r = r.json()
                logging.info(f"keys: {list(r.keys())}")
                summary = r['summary']
                results = r['documents']

                for doc in results:
                    self.list_of_docs.append(doc)

                self.paginate_docs(summary)

        return self.list_of_docs
    


    def paginate_docs(self, docs_summary: dict) -> None:
        """
        This function checks if there are documents remaining to be collected.
        """
        offset = docs_summary['offset']
        count = docs_summary['count']
        docs_remaining = docs_summary['totalItems'] - (offset + count)

        logger.info(f"Offset: {offset}\nCount: {count}\nDocs Remaining: {docs_remaining}")

        if docs_summary['hasMoreItems']:
            logger.info(f"There are {docs_remaining} documents remaining...")
            self.offset=docs_summary['offset'] + docs_summary['count'] 
        else:
            logger.info("There are no more docs to collect. Exiting...")
            self.has_more_items = False
        

# This part only runs when drs_utils.py is executed directly
if __name__ == "__main__":
    # Testing code
    drs = DRSUtils()
    # Call some methods of DRSUtils for testing
    drs.get_docs("AD")
    help(drs.get_docs)
