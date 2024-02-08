from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.s3 import S3
from os import path
import boto3
import pandas as pd
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

BUCKET = 'dez2024-dez-mage'


@data_loader
def load_from_s3_bucket(*args, **kwargs):
    """
    Template for loading data from a S3 bucket.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#s3
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'dev'

    config = ConfigFileLoader(config_path, config_profile)

    aws_credentials = {
        'aws_access_key_id': config.config['AWS_ACCESS_KEY_ID'],
        'aws_secret_access_key': config.config['AWS_SECRET_ACCESS_KEY']
    }

    s3_client = boto3.client(
        's3',
        **aws_credentials
    )

    response = s3_client.list_objects_v2(
        Bucket=BUCKET,
        Prefix='ny_taxi/green_taxi_data/'
    )

    df = pd.DataFrame()

    try:
        contents = response['Contents']
    except:
        print('NOTHING FOUND')
    else:
        for i in contents:
            if '.parquet' in i['Key']:
                df_i = S3.with_config(config).load(BUCKET, i['Key'])                
                df = pd.concat([df, df_i])

    df.reset_index(inplace=True, drop=True)

    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
