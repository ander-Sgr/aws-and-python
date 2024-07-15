import os
import pytest
import boto3
import time
from moto import mock_ec2
from main import create_ec2_client, create_ec2_resource, create_security_group, create_ec2_instance, \
    list_instances, delete_ec2_instance, EC2InstanceParams, exist_security_group


@pytest.fixture(scope='function')
def aws_credentials():
    """Fixture to set up mocked AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope='function')
def ec2_client(aws_credentials):
    with mock_ec2():
        yield boto3.client('ec2', region_name='us-east-1')


@pytest.fixture(scope='function')
def ec2_resource(aws_credentials):
    with mock_ec2():
        yield boto3.resource('ec2', region_name='us-east-1')


class EC2InstanceParams:
    def __init__(self):
        self.security_group_name = 'test-security-group'
        self.ami_id = 'ami-12345678'
        self.key_name = 'my-keypair'
        self.name_instance = 'TestInstance'


def setup_security_group(ec2_client, group_name):
    if not exist_security_group(ec2_client, group_name):
        create_security_group(ec2_client, group_name)


def test_create_ec2_instance(ec2_client, ec2_resource):
    setup_security_group(ec2_client, 'test-security-group')
    assert len(list_instances(ec2_client)) == 0
    params = EC2InstanceParams()
    instance_id, public_ip, instance_type = create_ec2_instance(ec2_client, ec2_resource, params)
    assert len(list_instances(ec2_client)) == 1
    assert instance_id is not None
    assert public_ip is not None
    assert instance_type == 't2.micro'
    instance = ec2_resource.Instance(instance_id)
    security_groups = [group['GroupName'] for group in instance.security_groups]
    assert 'test-security-group' in security_groups
    delete_ec2_instance(ec2_client, instance_id)
    time.sleep(5)
    assert len(list_instances(ec2_client)) == 1


def test_delete_ec2_instance(ec2_client, ec2_resource):
    setup_security_group(ec2_client, 'test-security-group')
    assert len(list_instances(ec2_client)) == 0
    params = EC2InstanceParams()
    instance_id, _, _ = create_ec2_instance(ec2_client, ec2_resource, params)
    assert len(list_instances(ec2_client)) == 1
    delete_ec2_instance(ec2_client, instance_id)
    time.sleep(5)
    assert len(list_instances(ec2_client)) == 1
