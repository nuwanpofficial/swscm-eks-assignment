import boto3
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'package'))
from crhelper import CfnResource

helper = CfnResource()

@helper.create
@helper.update
def create_update_resource(event, context):
    ssm_client = boto3.client('ssm')
    response = ssm_client.get_parameter(Name='/platform/account/env')
    env = response['Parameter']['Value']

    if env == 'development':
        replica_count = 1
    elif env == 'staging' or env == 'production':
        replica_count = 2
    else:
        replica_count = 0

    helper.Data.update({'replicaCount': replica_count})


@helper.delete
def delete_resource(event, context):
    pass

def handler(event, context):
    helper(event, context)