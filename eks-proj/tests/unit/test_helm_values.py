import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '../../lambda/helm_values'))
import helmval #type: ignore

## Defining Base Data for the test functions
@pytest.fixture
def ssm_mock_func():
    with patch('helmval.boto3.client') as mock_client:
        ssm_mock = MagicMock()
        mock_client.return_value = ssm_mock
        yield ssm_mock

@pytest.fixture
def helper_mock_func():
    with patch('helmval.helper') as helper_mock:
        helper_mock.Data = MagicMock()
        yield helper_mock


## Defining Test Function for the development enviornment values
@pytest.mark.parametrize("request_type", ["Create", "Update"])
def test_dev_env_actions(ssm_mock_func, helper_mock_func, request_type):
    ssm_mock_func.get_parameter.return_value = {
        'Parameter': {
            'Value': 'development'
        }
    }

    event = {'RequestType': request_type}
    context = MagicMock()

    result = helmval.create_update_resource(event, context)

    ssm_mock_func.get_parameter.assert_called_once_with(Name='/platform/account/env')

    helper_mock_func.Data.update.assert_called_once_with({'replicaCount': 1})

## Defining Test Function for the staging enviornment values
@pytest.mark.parametrize("request_type", ["Create", "Update"])
def test_staging_env_actions(ssm_mock_func, helper_mock_func, request_type):
    ssm_mock_func.get_parameter.return_value = {
        'Parameter': {
            'Value': 'staging'
        }
    }

    event = {'RequestType': request_type}
    context = MagicMock()

    result = helmval.create_update_resource(event, context)

    ssm_mock_func.get_parameter.assert_called_once_with(Name='/platform/account/env')

    helper_mock_func.Data.update.assert_called_once_with({'replicaCount': 2})


## Defining Test Function for the production enviornment values
@pytest.mark.parametrize("request_type", ["Create", "Update"])
def test_prod_env_actions(ssm_mock_func, helper_mock_func, request_type):
    ssm_mock_func.get_parameter.return_value = {
        'Parameter': {
            'Value': 'production'
        }
    }

    event = {'RequestType': request_type}
    context = MagicMock()

    result = helmval.create_update_resource(event, context)

    ssm_mock_func.get_parameter.assert_called_once_with(Name='/platform/account/env')

    helper_mock_func.Data.update.assert_called_once_with({'replicaCount': 2})


## Defining Test Function for the delete event of all environments
def test_delete_func(helper_mock_func):
    event = {'RequestType': 'Delete'}
    context = MagicMock()

    result = helmval.delete_resource(event, context)
    assert result is None

@pytest.mark.parametrize("request_type", ["Create", "Update"])
def test_main_func(helper_mock_func, request_type):
    event = {'RequestType': request_type}
    context = MagicMock()

    helmval.handler(event, context)
    helper_mock_func.assert_called_once_with(event, context)