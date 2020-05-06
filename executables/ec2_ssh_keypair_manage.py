import sys
import os
import json
import argparse
import pprint
import datetime
from utils.ec2_utils import AwsEc2


def main(aws_config, describe_ssh_keypair, create_ssh_keypair, delete_ssh_keypair, ssh_keypair_name):

    with open(aws_config, 'r') as f:
        aws_creds = json.load(f)

    # Initialize instance of AwsEc2 Class
    ec2 = AwsEc2(aws_creds['access_key_id'], 
                 aws_creds['secret_access_key'], 
                 aws_creds['aws_region'])

    if describe_ssh_keypair:
        response = ec2.describe_ssh_keypair()      
        print(json.dumps(response, default = ec2.date_time_converter ,indent=4))

    if create_ssh_keypair:
        response = ec2.create_delete_ssh_keypairs(keypair_name=ssh_keypair_name, action='create')
        print(json.dumps(response, default = ec2.date_time_converter ,indent=4))

    if delete_ssh_keypair:
        response = ec2.create_delete_ssh_keypairs(keypair_name=ssh_keypair_name, action='delete')
        print(json.dumps(response, default = ec2.date_time_converter ,indent=4))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws_config', required=False, 
                        default='C:\\Users\\Nikola Naydenov\\Desktop\\AWS\\.config\\.aws_config.json', 
                        help='AWS credentials config file path')
    
    parser.add_argument('--describe_ssh_keypair', action='store_true', 
                        help="Described SSH key pairs")
    
    parser.add_argument('--create_ssh_keypair', action='store_true', help='create SSH key pairs')   
    parser.add_argument('--delete_ssh_keypair', action='store_true', help='delete SSH key pairs')
    parser.add_argument('--ssh_keypair_name', required=False, help='SSH key pair name to be created/deleted')
    
    args = parser.parse_args()

    if args.create_ssh_keypair and not args.ssh_keypair_name:
        raise AttributeError(f"'--ssh_keypair_name' not provided and dependent to '--create_ssh_keypair'.")
    elif args.delete_ssh_keypair and not args.ssh_keypair_name:
        raise AttributeError(f"'--ssh_keypair_name' not provided and dependent to '--delete_ssh_keypair'.")
    
    main(args.aws_config, args.describe_ssh_keypair, args.create_ssh_keypair, args.delete_ssh_keypair, args.ssh_keypair_name)
