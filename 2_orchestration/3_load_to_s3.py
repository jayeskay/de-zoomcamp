from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.s3 import S3
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

BUCKET = 'dez2024-dez-mage'
PREFIX = 'ny_taxi/green_taxi_data/green_taxi_data_2020Q4'

@data_exporter
def export_data_to_s3(df: DataFrame, **kwargs) -> None:
    """
    Template for exporting data to a S3 bucket.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#s3
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'dev'

    for date in df['lpep_pickup_date'].unique():
        df_partitioned = df[df['lpep_pickup_date'] == date]

        S3.with_config(ConfigFileLoader(config_path, config_profile)).export(
            df=df_partitioned,
            bucket_name=BUCKET,
            object_key=f"{PREFIX}_{date.strftime('%Y%m%d')}.parquet"
        )
