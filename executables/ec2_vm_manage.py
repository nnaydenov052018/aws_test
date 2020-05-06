import sys
import os
import json
import argparse
import pprint
import datetime
from utils.ec2_utils import AwsEc2

def main(aws_config, describe_ec2, create_ec2, image_id, instance_type,
         ssh_keypair_name, min_count, max_count, user_data, terminate_ec2,
         action, ec2_ids, exec_shell, ec2_public_ip, ec2_user,
         ssh_private_key, cmd):

    with open(aws_config, 'r') as f:
        aws_creds = json.load(f)

    # Initialize instance of AwsEc2 Class
    ec2 = AwsEc2(aws_creds['access_key_id'], 
                 aws_creds['secret_access_key'], 
                 aws_creds['aws_region'])

    if describe_ec2:
        response = ec2.describe_ec2_instances()
        print(json.dumps(response, default = ec2.date_time_converter ,indent=4))

    if create_ec2:
        with open(user_data, 'r') as f:
            UserDataString = f.read()
        
        instance_info = ec2.create_ec2_instance(image_id = image_id, 
                                                instance_type = instance_type, 
                                                keypair_name = ssh_keypair_name, 
                                                mincount = min_count, 
                                                maxcount = max_count, 
                                                UserData = UserDataString)
        
        if instance_info is not None:
            print(f'Launched EC2 Instance {instance_info["InstanceId"]}')
            print(f'    VPC ID: {instance_info["VpcId"]}')
            print(f'    Private IP Address: {instance_info["PrivateIpAddress"]}')
            print(f'    Current State: {instance_info["State"]["Name"]}')

    if terminate_ec2:
        ec2_to_terminate = terminate_ec2.split(',')
        terminate = ec2.terminate_ec2_instances(ec2_to_terminate)
        print(terminate)
    
    if action and ec2_ids:
        ec2_to_manage = ec2_ids.split(',')
        ec2.start_stop_reboot_ec2_instances(ec2_to_manage, action)

    if exec_shell:
        if os.path.isfile(cmd):
            with open(cmd, 'r') as f:
                shell_script = f.read()
        
        else:
            shell_script = f"""
            #!/bin/bash
            {cmd}
            """

        ec2.ec2_exec_shell(instance_ip = ec2_public_ip, 
                           ec2_user = ec2_user, 
                           ssh_private_key = ssh_private_key, 
                           cmd = shell_script)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws_config', required=False, default='C:\\Users\\Nikola Naydenov\\Desktop\\AWS\\.config\\.aws_config.json', 
                        help='AWS credentials config file path')
    # Describe EC2
    parser.add_argument('--describe_ec2', action='store_true', help='describe EC2 instance')
    
    # Create EC2
    parser.add_argument('--create_ec2', action='store_true', help='create EC2 instance')
    parser.add_argument('--image_id', required=False, default='ami-076431be05aaf8080', help='EC2 image id')
    parser.add_argument('--instance_type', required=False, default='t2.micro', help='EC2 instance type')
    parser.add_argument('--ssh_keypair_name', required=False, default='devops-ssh', help='ssh key pair to be used by EC2')
    parser.add_argument('--min_count', required=False, default=1, help='Min count of EC2 instances to be provisioned')
    parser.add_argument('--max_count', required=False, default=1, help='Max count of EC2 instances to be provisioned')
    parser.add_argument('--user_data', required=False, default='.\\EC2\\UserData\\install_docker.sh', help='Path to User Data script')

    # Terminate EC2
    parser.add_argument('--terminate_ec2', required=False, help='EC2 instance ids to be terminated ,comma delimited')
    
    # Start/Stop/Restart EC2
    parser.add_argument('--action', required=False, 
                        help="Start/Stop/Reboot EC2. Valid actions: ON|OFF|REBOOT|RESTART")
    parser.add_argument('--ec2_ids', required=False, help='EC2 instance ids to be managed ,comma delimited')

    # Exec shell command/script on EC2
    parser.add_argument('--exec_shell', action='store_true', help='Execute shell command/script on EC2')
    parser.add_argument('--ec2_public_ip', required=False, help='public IP of EC2')
    parser.add_argument('--ec2_user', required=False, default='ec2-user', help='EC2 user to run command/script')
    parser.add_argument('--ssh_private_key', required=False, default='C:\\Users\\Nikola Naydenov\\Desktop\\AWS\\.ssh\\devops-ssh.pem', 
                        help='path to ssh private key for EC2')
    parser.add_argument('--cmd', required=False, help='command/script to run')


    args = parser.parse_args()

    warn_message = "--create_ec2 requires: --image_id --instance_type --ssh_keypair_name --min_count --max_count --user_data" 
    if args.create_ec2 and not args.image_id:
        raise AttributeError(f"'--image_id' not provided and dependent to '--create_ec2'. {warn_message}")
    elif args.create_ec2 and not args.instance_type:
        raise AttributeError(f"'--instance_type' not provided and dependent to '--create_ec2'. {warn_message}")
    elif args.create_ec2 and not args.ssh_keypair_name:
        raise AttributeError(f"'--ssh_keypair_name' not provided and dependent to '--create_ec2'. {warn_message}")
    elif args.create_ec2 and not args.min_count:
        raise AttributeError(f"'--min_count' not provided and dependent to '--create_ec2'. {warn_message}")
    elif args.create_ec2 and not args.max_count:
        raise AttributeError(f"'--max_count' not provided and dependent to '--create_ec2'. {warn_message}")
    elif args.create_ec2 and not args.user_data:
        raise AttributeError(f"'--user_data' not provided and dependent to '--create_ec2'. {warn_message}")
    
    if args.action and not args.ec2_ids:
        raise AttributeError("'--ec2_ids' not provided and dependent to '--action'. --action requires --ec2_ids")

    warn_message_sh = "--exec_shell requires: --ec2_public_ip --ec2_user --ssh_private_key --cmd" 
    if args.exec_shell and not args.ec2_public_ip:
        raise AttributeError(f"'--ec2_public_ip' not provided and dependent to '--exec_shell'. {warn_message_sh}")
    elif args.exec_shell and not args.ec2_user:
        raise AttributeError(f"'--ec2_user' not provided and dependent to '--exec_shell'. {warn_message_sh}")
    elif args.exec_shell and not args.ssh_private_key:
        raise AttributeError(f"'--ssh_private_key' not provided and dependent to '--exec_shell'. {warn_message_sh}")
    elif args.exec_shell and not args.cmd:
        raise AttributeError(f"'--cmd' not provided and dependent to '--exec_shell'. {warn_message_sh}")

    main(args.aws_config, args.describe_ec2, args.create_ec2, args.image_id, args.instance_type, 
         args.ssh_keypair_name, args.min_count, args.max_count, args.user_data, args.terminate_ec2,
         args.action, args.ec2_ids, args.exec_shell, args.ec2_public_ip, args.ec2_user, 
         args.ssh_private_key, args.cmd)
