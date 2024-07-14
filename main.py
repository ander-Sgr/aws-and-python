import sys
import boto3
from typing import List

from argparse import ArgumentParser, Namespace

from boto3 import ec2


def parser_args(args: List) -> Namespace:
    parser = ArgumentParser("AWS EC2: Create and manage EC2 instances")
    parser.add_argument('-c', '--create', action='store_true', help='Create a new EC2 instances')
    parser.add_argument('-n', '--name', type=str, help='Name of an existing EC2 instance')
    parser.add_argument('-a', '--ami-id', type=str, help='Id of the Amazon machine')
    parser.add_argument('-k', '--key-name', type=str, help="Name of the key pair for SSH access")
    parser.add_argument('-r', '--region', type=str, help="The region of the instance EC2")
    parser.add_argument('-l', '--list', action='store_true', help='List all EC2 instances')
    parser.add_argument('-d', '--destroy', action='store_true', help='Destroy an existing EC2 instance')
    return parser.parse_args(args)


def create_ec2_client():
    return boto3.client('ec2', region_name='us-east-1')


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


def create_ec2_instance(ec2_client, name_instance: str, ami_id: str, key_name: str, region_name: str):
    ec2_resource = boto3.resource('ec2', region_name)
    response = ec2_resource.create_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=key_name,
        SecurityGroups=[create_security_group(ec2_client)],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': name_instance
                    }
                ]
            }
        ]
    )[0]
    response.wait_until_running()
    response.reload()

    return response.id, response.public_ip_address


def exist_security_group(ec2_client, group_name: str, region_name: str) -> bool:
    response = ec2_client.describe_security_groups(
        Filters=[
            {"Name": "group-name", "Values": [group_name]},
        ]
    )
    if response['SecurityGroups']:
        return True
    else:
        return False


def main(args: list):
    parsed_args = parser_args(args)
    ec2_client = create_ec2_client()

    if (parsed_args.create and parsed_args.name and parsed_args.ami_id
            and parsed_args.key_name) and parsed_args.region:
        security_group_id = create_security_group(ec2_client)
        print(f"Created security group with ID: {security_group_id}")
        instance_id, public_ip = create_ec2_instance(ec2_client, parsed_args.name,
                                                     parsed_args.ami_id, parsed_args.key_name, parsed_args.region)
    else:
        print("Invalid input: Use -h or --hel for see the instructions ")


if __name__ == '__main__':
    main(sys.argv[1:])
