import os
import boto3

DYNAMO_ENDPOINT = os.getenv("DYNAMO_ENDPOINT", None)  # para localstack
REGION = os.getenv("AWS_REGION", "us-east-1")

def get_dynamo():
    if DYNAMO_ENDPOINT:
        return boto3.resource("dynamodb", region_name=REGION, endpoint_url=DYNAMO_ENDPOINT)
    return boto3.resource("dynamodb", region_name=REGION)
