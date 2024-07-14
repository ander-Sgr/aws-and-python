import sys
import boto3
from typing import List

from argparse import ArgumentParser, Namespace

from boto3 import ec2


class EC2InstanceParams:
    def __init__(self, name_instance: str, ami_id: str, key_name: str,
                 security_group_name: str, type_instance: str):
        self.name_instance = name_instance
        self.ami_id = ami_id
        self.key_name = key_name
        self.type_instance = type_instance
        self.security_group_name = security_group_name
        # self.region_name = region_name


def parser_args(args: List) -> Namespace:
    parser = ArgumentParser("AWS EC2: Create and manage EC2 instances")
    parser.add_argument('-c', '--create', action='store_true',
                        help='Create a new EC2 instances')
    parser.add_argument('-n', '--name', type=str,
                        help='Name for assign to EC2 instance')
    parser.add_argument('-a', '--ami-id', type=str,
                        help='Id of the Amazon machine')
    parser.add_argument('-k', '--key-name', type=str,
                        help="Name of the key pair for SSH access")
    # parser.add_argument('-r', '--region', type=str,
    #                   help="The region of the instance EC2")
    parser.add_argument('-t', '--type-instance', type=str, default='t2.micro',
                        help="Type of instance")
    parser.add_argument('-l', '--list', action='store_true',
                        help='List all EC2 instances')
    parser.add_argument('-d', '--destroy', action='store_true',
                        help='Destroy an existing EC2 instance')
    return parser.parse_args(args)


def create_ec2_client(region_name: str):
    return boto3.client('ec2', region_name=region_name)


def create_ec2_resource(region_name: str):
    return boto3.resource('ec2', region_name=region_name)


def create_security_group(ec2_client, group_name: str) -> str:
    response = ec2_client.create_security_group(
        GroupName=group_name,
        Description='Allow SSH access to EC2 instances',
    )
    security_group_id = response['GroupId']

    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
            }
        ]

    )

    return security_group_id


def init_instance_params(parsed_args: Namespace) -> EC2InstanceParams:
    return EC2InstanceParams(
        name_instance=parsed_args.name,
        ami_id=parsed_args.ami_id,
        key_name=parsed_args.key_name,
        type_instance=parsed_args.type_instance,
        security_group_name='SSHAccess',
        # region_name=parsed_args.region
    )


def exist_security_group(ec2_client, group_name: str) -> bool:
    response = ec2_client.describe_security_groups(
        Filters=[
            {"Name": "group-name", "Values": [group_name]},
        ]
    )
    if response['SecurityGroups']:
        return True
    else:
        return False


def create_ec2_instance(ec2_client, ec2_resource, params: EC2InstanceParams):
    if not exist_security_group(ec2_client, params.security_group_name):
        security_group_id = create_security_group(ec2_client, params.security_group_name)
        print(f"Created security group with ID: {security_group_id}")

    response = ec2_resource.create_instances(
        ImageId=params.ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=params.key_name,
        SecurityGroups=[params.security_group_name],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': params.name_instance
                    }
                ]
            }
        ]
    )[0]
    response.wait_until_running()
    response.reload()

    return response.id, response.public_ip_address, response.instance_type


def main(args: list):
    parsed_args = parser_args(args)
    ec2_client = create_ec2_client('us-east-1')
    ec2_resource = create_ec2_resource('us-east-1')

    if parsed_args.create and parsed_args.name and parsed_args.ami_id \
            and parsed_args.key_name and parsed_args.type_instance:
        params = EC2InstanceParams(
            name_instance=parsed_args.name,
            ami_id=parsed_args.ami_id,
            key_name=parsed_args.key_name,
            security_group_name='SSHAccess-test',
            type_instance=parsed_args.type_instance
        )
        instance_id, public_ip, instance_type = create_ec2_instance(ec2_client, ec2_resource, params)
        print(f"Created EC2 instance with ID: {instance_id} Public IP: {public_ip} "
              f" Type of instance: {instance_type}")
    else:
        print("Invalid input: Use -h or --hel for see the instructions ")


if __name__ == '__main__':
    main(sys.argv[1:])
