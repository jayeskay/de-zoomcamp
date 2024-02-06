import pandas as pd
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """

    files = [
        'green_tripdata_2020-10.csv.gz',
        'green_tripdata_2020-11.csv.gz',
        'green_tripdata_2020-12.csv.gz'
    ]

    url_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/'

    green_taxi_data_dtypes = {
        'VendorID': pd.Int64Dtype(),
        'lpep_pickup_datetime': str,
        'lpep_dropoff_datetime': str,
        'store_and_fwd_flag': str,
        'RatecodeID': pd.Int64Dtype(),
        'PULocationID': pd.Int64Dtype(),
        'DOLocationID': pd.Int64Dtype(),
        'passenger_count': pd.Int64Dtype(),
        'trip_distance': float,
        'fare_amount': float,
        'extra': float,
        'mta_tax': float,
        'tip_amount': float,
        'tolls_amount': float,
        'ehail_fee': float,
        'improvement_surcharge': float,
        'total_amount': float,
        'payment_type': pd.Int64Dtype(),
        'trip_type ': pd.Int64Dtype(),
        'congestion_surcharge': float
    }

    green_taxi_data_datetimes = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']

    green_taxi_data = pd.DataFrame()

    for csv_gz in files:
        url = url_prefix + csv_gz

        df = pd.read_csv(
            url,
            sep=',',
            compression='gzip',
            dtype=green_taxi_data_dtypes,
            parse_dates=green_taxi_data_datetimes
        )

        green_taxi_data = pd.concat([green_taxi_data, df])

    return green_taxi_data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
