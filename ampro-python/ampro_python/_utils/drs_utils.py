import os
import requests
import logging
from dotenv import load_dotenv
import logging

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

            
    def _call_drs(self):
        logger.info(f"\n{'*'*50}\n_call_drs")
        
        endpoint = self._get_endpoint()
        headers = {"x-api-key": self.drs_api_key}
        payload = {
            "offset": self.offset
            # docLastModifiedDate = strptime(doc_last_modified, date_format)
        }
        request_url = f"{self.base_url}{endpoint}"

        try:
            logger.info("Calling API...")
            r = requests.get(request_url, headers=headers, params=payload)
        except Exception as e:
            logger.exception(f"Exception: {e} while calling API")

        return r

    def get_docs(
        self,
        doc_type: str = "AD",
        offset: int = 0,
        doc_last_modified: str = None,
        paginate: bool = True,
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
        logger.info(f"****\nget_docs\n\nDocument: {doc_type}\nOffset: {offset}\nPaginate: {paginate}")
        self.offset = offset
        self.doc_type = doc_type
        self.paginate=paginate

        logger.info(
            f"Calling `get_docs` with the following params: \ndoc_type: {self.doc_type}\noffset: {self.offset}"
        )

        while True:
            self.paginate=paginate
            logger.info(f"\n\nPaginate: {self.paginate}\n\n")
    
            r = self._call_drs()
    
            if not r.raise_for_status():
                r = r.json()
                # logger.info(f"keys: {list(r.keys())}")
                summary = r["summary"]
                results = r["documents"]
    
                for doc in results:
                    self.list_of_docs.append(doc)
    
                if self.paginate:
                    self.paginate_docs(summary)
                else:
                    break

        return self.list_of_docs



# This part only runs when drs_utils.py is executed directly
if __name__ == "__main__":
    # Testing code
    drs = DRSUtils()
    # Call some methods of DRSUtils for testing
    drs.get_docs("AD")
    help(drs.get_docs)
