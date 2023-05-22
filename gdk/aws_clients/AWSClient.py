import boto3

service_clients = {}


def ssm(region_name="us-east-1"):
    return _get_client("ssm", region_name)


def sts(region_name=None):
    return _get_client("sts", region_name)


def _get_client(_service_name, _region_name):
    _client = service_clients.get(_service_name, {})
    if not _client.get(_region_name, None):
        service_clients.update({_service_name: {_region_name: boto3.client(_service_name, region_name=_region_name)}})
    return service_clients[_service_name][_region_name]
