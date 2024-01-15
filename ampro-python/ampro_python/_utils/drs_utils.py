import os
import requests
import logging
from typing import Union
from dotenv import load_dotenv

load_dotenv()

base_url = "https://drs.faa.gov/api/drs/data-pull/"

class DRSUtils:
    def __init__(self):
        self.drs_api_key = os.getenv("DRS_API_KEY")
        self.date_format = '%y-%m-%dT%H:%M:%S.%fffZ'
        self.offset = 0

    def get_docs(self, 
            doc_type: str = "AD", 
            offset: int = 0, 
            doc_last_modified: str = None
            ) -> None:
        """
        This function collects all documents of a specified type.
        See README.md for additional types.

        Params
        ------
        default                     Collects ADs, ACs, and EADs.
        AD | ad      ADNPRM         Airworthiness Directives
        AC | ac      AC             Advisory Circulars     
        EAD          ADFREAD        Emergency ADs

        """
        if doc_type.lower() == 'ad':
            request_url = f"{base_url}ADNPRM"
        elif doc_type.lower() =='ac':
            request_url = f"{base_url}AC"
        elif doc_type.lower() == 'ead':
            request_url = f"{base_url}ADFREAD"

        headers = {
                'x-api-key': self.drs_api_key
                }

        payload = {
                'offset': offset 
                #docLastModifiedDate = strptime(doc_last_modified, date_format)
                }       

        #        print(f"Request URL: {request_url}\nOffset: {offset}\nDate Format: {self.date_format}")


        
        #r = requests.get(base_url

        print(f"Request URL: {request_url}\nOffset: {offset}\nDate Format: {self.date_format}")
# This part only runs when drs_utils.py is executed directly
if __name__ == "__main__":
    # Testing code
    drs = DRSUtils()
    # Call some methods of DRSUtils for testing
    drs.get_docs("AD")
    help(drs.get_docs)
