if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    print("Preprocessing: rows with zero passengers:", data['passenger_count'].isin([0]).sum())
    print("Preprocessing: trip distance is equal to zero:", data['trip_distance'].isin([0]).sum())

    data_transformed = data[(data['passenger_count'] > 0) & (data['trip_distance'] > 0) & (data['VendorID'].isin([1, 2]))]

    data_transformed['lpep_pickup_date'] = data_transformed['lpep_pickup_datetime'].dt.date
    data_transformed['lpep_pickup_time'] = data_transformed['lpep_pickup_datetime'].dt.time
    data_transformed['lpep_dropoff_date'] = data_transformed['lpep_dropoff_datetime'].dt.date
    data_transformed['lpep_dropoff_time'] = data_transformed['lpep_dropoff_datetime'].dt.time

    return data_transformed


@test
def test_passenger_count(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output[output['passenger_count'] == 0]['passenger_count'].count() == 0, 'There are rides with zero passengers'


@test
def test_ride_distance(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output[output['trip_distance'] == 0]['trip_distance'].count() == 0, 'There are trips with zero distance'


@test
def test_vendor_ids(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output[~output['VendorID'].isin([1, 2])]['VendorID'].count() == 0, 'There are unrecognized vendor IDs'
