import sys
import os
import json
import argparse
import pprint
import datetime
from utils.ec2_utils import AwsEc2


def main(aws_config, describe_sg, create_sg, 
         sg_name, sg_ingress_ports, delete_sg, 
         sg_to_attach_to_ec2, ec2_ids):

    with open(aws_config, 'r') as f:
        aws_creds = json.load(f)

    # Initialize instance of AwsEc2 Class
    ec2 = AwsEc2(aws_creds['access_key_id'], 
                 aws_creds['secret_access_key'], 
                 aws_creds['aws_region'])

    if describe_sg:
        if describe_sg == '*':
            response = ec2.describe_ec2_security_groups(security_group_ids=describe_sg)
        else:
            sg_to_describe = describe_sg.split(',')
            response = ec2.describe_ec2_security_groups(security_group_ids=sg_to_describe)
        
        print(json.dumps(response, default = ec2.date_time_converter ,indent=4))

    if create_sg:
       ingress_ports = sg_ingress_ports.split(',')
       ec2.create_ec2_security_group(security_group_name=sg_name, ingress_port=ingress_ports)

    if delete_sg:
        sg_to_del = delete_sg.split(',')
        for sg_id in sg_to_del:
            ec2.delete_ec2_security_group(security_group_id=sg_id)
    
    if sg_to_attach_to_ec2 and ec2_ids:
        sgs = sg_to_attach_to_ec2.split(',')
        ec2s = ec2_ids.split(',')
        ec2.change_ec2_security_groups(instance_ids=ec2s, security_group_ids=sgs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws_config', required=False, default='C:\\Users\\Nikola Naydenov\\Desktop\\AWS\\.config\\.aws_config.json', 
                        help='AWS credentials config file path')
    
    parser.add_argument('--describe_sg', required=False, help="SG ids to be described ,comma delimited. To describe all available SGs use '*' ")
    
    parser.add_argument('--create_sg', action='store_true', help='create SG')
    parser.add_argument('--sg_name', required=False, help='SG name')
    parser.add_argument('--sg_ingress_ports', required=False, help='SG ingress ports ,comma delimited')
    
    parser.add_argument('--delete_sg', required=False, help='SG ids to be deleted ,comma delimited')
    
    parser.add_argument('--sg_to_attach_to_ec2', required=False, 
                        help="Attach SG to EC2 instance. SG ids ,comma delimited")
    parser.add_argument('--ec2_ids', required=False, help='EC2 instance ids to be attach SGs ,comma delimited')

    args = parser.parse_args()

    warn_message = "--create_sg requires: --sg_name --sg_ingress_ports" 
    if args.create_sg and not args.sg_name:
        raise Exception(f"'--sg_name' not provided and dependent to '--create_sg'. {warn_message}")
    elif args.create_sg and not args.sg_ingress_ports:
        raise Exception(f"'--sg_ingress_ports' not provided and dependent to '--create_sg'. {warn_message}")
    
    if args.sg_to_attach_to_ec2 and not args.ec2_id:
        raise Exception("'--ec2_ids' not provided and dependent to '--sg_to_attach_to_ec2'. --sg_to_attach_to_ec2 requires --ec2_ids")

    main(args.aws_config, args.describe_sg, args.create_sg, args.sg_name, args.sg_ingress_ports, 
         args.delete_sg, args.sg_to_attach_to_ec2, args.ec2_ids)
