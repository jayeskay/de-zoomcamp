import dlt
import duckdb
import requests
import pandas as pd
from bs4 import BeautifulSoup
from boto3 import Session
from io import BytesIO
from typing import Generator


# extract
def stream_download_parquet(url, dtypes) -> Generator[pd.DataFrame, None, None]:
    response = requests.get(url).text
    soup = BeautifulSoup(response, features='html.parser')  # Raise an HTTPError for bad responses

    for i, link in enumerate(soup.findAll('a')):
        href = link.get('href')

        if 'fhv_tripdata_2019' in href:
            parquet_file = pd.read_parquet(href)
            
            yield parquet_file.astype(dtypes)


# load
def stream_upload_parquet(df: pd.DataFrame, bucket: str, object_key: str) -> None:
    session = Session(profile_name='dez')
    s3_client = session.client('s3')

    # https://stackoverflow.com/questions/53416226/how-to-write-parquet-file-from-pandas-dataframe-in-s3-in-python
    out_buffer = BytesIO()
    df.to_parquet(out_buffer, compression='gzip', index=False)

    s3_client.put_object(Bucket=bucket, Key=object_key, Body=out_buffer.getvalue())


if __name__ == '__main__':
    url = 'https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page'

    dtypes = {
        'dispatching_base_num':     str,
        'pickup_datetime':          str,
        'dropOff_datetime':         str,
        'PUlocationID':             pd.Int64Dtype(),
        'DOlocationID':             pd.Int64Dtype(),
        'SR_Flag':                  pd.Int64Dtype(),
        'Affiliated_base_number':   str
    }

    generators_pipeline = dlt.pipeline(
        destination='duckdb',
        dataset_name='generators'
    )

    info = generators_pipeline.run(
        stream_download_parquet(url=url, dtypes=dtypes),
        table_name='stream_download',
        write_disposition='replace'
    )

    print(info)

    with duckdb.connect(f"{generators_pipeline.pipeline_name}.duckdb") as conn:

        # show tables
        conn.sql(f"SET search_path = '{generators_pipeline.dataset_name}'")
        print('Loaded tables:')
        conn.sql('show tables').show()

        # show data
        print('stream_download table below:')
        conn.sql('SELECT * FROM stream_download LIMIT 5').show()

        # count records
        print('stream_download count of records:')
        conn.sql('SELECT COUNT(*) FROM stream_download').show()

        query_group_by_date = '''
            SELECT
                pickup_datetime::DATE AS pickup_date,
                COUNT(*) AS count
                
            FROM
                stream_download
                
            GROUP BY
                pickup_datetime::DATE
                
            ORDER BY
                pickup_datetime::DATE
        '''

        duck_df = conn.sql(query_group_by_date).df()

        print(duck_df.head())

        BUCKET = 'dez2024-dez-dlt'
        PREFIX = 'ny_taxi/fhv/2019'

        for d in duck_df['pickup_date']:
            stream_upload_parquet(
                df=conn.sql(f"SELECT * FROM stream_download WHERE pickup_datetime::DATE = '{d.date()}'").df(),
                bucket=BUCKET,
                object_key=f"{PREFIX}/{d.strftime('%Y%m%d')}.parquet.gz"
            )
