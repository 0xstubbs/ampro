import utils.drs_utils as drs
from utils.drs_ingest import parse_documents


def main():
    #    DRS_API_KEY = os.getenv("DRS_API_KEY")

    drs_records = drs.drs_utils()
    data = drs_records.get_records()

    parse_documents(data)


if __name__ == "__main__":
    main()
