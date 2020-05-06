import logging
import json
import paramiko
import datetime
import boto3
from botocore.exceptions import ClientError


class AwsEc2(object):

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region

        self.ec2_client = boto3.client('ec2', 
                                        aws_access_key_id = self.aws_access_key_id,
                                        aws_secret_access_key = self.aws_secret_access_key,
                                        region_name=self.aws_region)

    def date_time_converter(self, o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def create_ec2_instance(self, image_id=None, instance_type=None, keypair_name=None, mincount=None, maxcount=None, UserData=None):
        # Provision and launch the EC2 instance
        try:
            response = self.ec2_client.run_instances(ImageId=image_id,
                                                InstanceType=instance_type,
                                                KeyName=keypair_name,
                                                MinCount=mincount,
                                                MaxCount=maxcount,
                                                UserData=UserData)

        except ClientError as e:
            logging.error(e)
            return None
        return response['Instances'][0]
    
    def terminate_ec2_instances(self, instance_ids):
        # Terminate each instance in the argument list
        try:
            states = self.ec2_client.terminate_instances(InstanceIds=instance_ids)
        except ClientError as e:
            logging.error(e)
            return None
        return states['TerminatingInstances']

    def describe_ec2_instances(self):
        response = self.ec2_client.describe_instances()
        return response
    
    def start_stop_reboot_ec2_instances(self, instance_id=None, action=None):
        if action.upper() == 'ON':
            # Do a dryrun first to verify permissions
            try:
                self.ec2_client.start_instances(InstanceIds=instance_id, DryRun=True)
            except ClientError as e:
                if 'DryRunOperation' not in str(e):
                    raise

            # Dry run succeeded, run start_instances without dryrun
            try:
                response = self.ec2_client.start_instances(InstanceIds=instance_id, DryRun=False)
                print(response)
            except ClientError as e:
                print(e)
        
        elif action.upper() == 'OFF':
            # Do a dryrun first to verify permissions
            try:
                self.ec2_client.stop_instances(InstanceIds=instance_id, DryRun=True)
            except ClientError as e:
                if 'DryRunOperation' not in str(e):
                    raise

            # Dry run succeeded, call stop_instances without dryrun
            try:
                response = self.ec2_client.stop_instances(InstanceIds=instance_id, DryRun=False)
                print(response)
            except ClientError as e:
                print(e)
        
        elif action.upper() == 'REBOOT' or action.upper() == 'RESTART':
            try:
                self.ec2_client.reboot_instances(InstanceIds=instance_id, DryRun=True)
            except ClientError as e:
                if 'DryRunOperation' not in str(e):
                    print("You don't have permission to reboot instances.")
                    raise

            try:
                response = self.ec2_client.reboot_instances(InstanceIds=instance_id, DryRun=False)
                print('Success', response)
            except ClientError as e:
                print('Error', e)
        
        else:
            raise Exception(f"Invalid action. Must be on|off|reboot|restart")

    def create_delete_ssh_keypairs(self, keypair_name=None, action=None):
        try:
            if action.upper() == 'CREATE':
                response = self.ec2_client.create_key_pair(KeyName=keypair_name)
                
            elif action.upper() == 'DELETE':
                response = self.ec2_client.delete_key_pair(KeyName=keypair_name)
        
            else:
                raise Exception(f"Invalid action. Must be create|delete")

            if response: return response
        
        except ClientError as e:
            print('Error', e)


    def describe_ssh_keypair(self):
        response = self.ec2_client.describe_key_pairs()
        return response

    def ec2_exec_shell(self, instance_ip=None, ec2_user=None, ssh_private_key=None, cmd=None):
        key = paramiko.RSAKey.from_private_key_file(ssh_private_key)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect/ssh to an instance
        try:
            # Here 'ec2_user' is user name and 'instance_ip' is public IP of EC2
            client.connect(hostname=instance_ip, username=ec2_user, pkey=key)

            # Execute a command(cmd) after connecting/ssh to an instance
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read())

            # close the client connection once the job is done
            client.close()

        except Exception as e:
            print('Error', e)
    
    def describe_ec2_security_groups(self, security_group_ids=None):
        try:
            if security_group_ids == '*': 
                response = self.ec2_client.describe_security_groups()
            else:
                response = self.ec2_client.describe_security_groups(GroupIds=security_group_ids)
            
            return response
        except ClientError as e:
            print('Error', e)

    def create_ec2_security_group(self, security_group_name=None, ingress_port=None):
        ip_permissions = []
        for port in ingress_port:
            fw_rule_dt = {'IpProtocol': 'tcp',
                          'FromPort': port,
                          'ToPort': port,
                          'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            
            ip_permissions.append(fw_rule_dt)
        
        response = self.ec2_client.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

        try:
            response = self.ec2_client.create_security_group(GroupName=security_group_name,
                                                             Description='New Security group',
                                                             VpcId=vpc_id)
            security_group_id = response['GroupId']
            print(f'Security Group Created {security_group_id} in vpc {vpc_id}.')

            data = self.ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=ip_permissions)
            print(f'Ingress Successfully Set {data}')
        except ClientError as e:
            print(e)
    
    def delete_ec2_security_group(self, security_group_id=None):
        # Delete security group
        try:
            response = self.ec2_client.delete_security_group(GroupId=security_group_id)
            print('Security Group Deleted')
        except ClientError as e:
            print(e)


    def change_ec2_security_groups(self, instance_ids=None, security_group_ids=None):
        for instance_id in instance_ids:
            try:
                response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            except ClientError as e:
                logging.error(e)
                return False
            instance_info = response['Reservations'][0]['Instances'][0]

            # Assign the security groups to each network interface
            for network_interface in instance_info['NetworkInterfaces']:
                try:
                    self.ec2_client.modify_network_interface_attribute(
                        NetworkInterfaceId=network_interface['NetworkInterfaceId'],
                        Groups=security_group_ids)
                except ClientError as e:
                    logging.error(e)
                    return False
        
        return True


