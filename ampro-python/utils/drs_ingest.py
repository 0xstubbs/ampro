import polars as pl


def parse_documents(drs_records: list[dict[str, str]]):
    df = pl.DataFrame(drs_records)
    print(df)
