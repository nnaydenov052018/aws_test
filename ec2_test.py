import logging
import json
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

    def create_ec2_instance(self, image_id=None, instance_type=None, keypair_name=None, mincount=None, maxcount=None):
        # Provision and launch the EC2 instance
        try:
            response = self.ec2_client.run_instances(ImageId=image_id,
                                                InstanceType=instance_type,
                                                KeyName=keypair_name,
                                                MinCount=mincount,
                                                MaxCount=maxcount)

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
    
    def start_stop_ec2_instances(self, instance_id=None, action=None):
        if action.upper() == 'ON':
            # Do a dryrun first to verify permissions
            try:
                self.ec2_client.start_instances(InstanceIds=[instance_id], DryRun=True)
            except ClientError as e:
                if 'DryRunOperation' not in str(e):
                    raise

            # Dry run succeeded, run start_instances without dryrun
            try:
                response = self.ec2_client.start_instances(InstanceIds=[instance_id], DryRun=False)
                print(response)
            except ClientError as e:
                print(e)
        else:
            # Do a dryrun first to verify permissions
            try:
                self.ec2_client.stop_instances(InstanceIds=[instance_id], DryRun=True)
            except ClientError as e:
                if 'DryRunOperation' not in str(e):
                    raise

            # Dry run succeeded, call stop_instances without dryrun
            try:
                response = self.ec2_client.stop_instances(InstanceIds=[instance_id], DryRun=False)
                print(response)
            except ClientError as e:
                print(e)


## Create class instance
with open('.config\\.config.json') as f:
  aws_creds = json.load(f)
ec2 = AwsEc2(aws_creds['access_key_id'], aws_creds['secret_access_key'], aws_creds['aws_region'])

## Describe instances
response = ec2.describe_ec2_instances()
print(response)

## Terminate instances
# terminate = ec2.terminate_ec2_instances(['i-0804ba3592cc35489'])
# print(terminate)

## Create instances
# instance_info = ec2.create_ec2_instance('ami-076431be05aaf8080', 't2.micro', 'test-nnaydenov', 2, 4)
# if instance_info is not None:
#     print(f'Launched EC2 Instance {instance_info["InstanceId"]}')
#     print(f'    VPC ID: {instance_info["VpcId"]}')
#     print(f'    Private IP Address: {instance_info["PrivateIpAddress"]}')
#     print(f'    Current State: {instance_info["State"]["Name"]}')

## Start/Stop instances
# ec2.start_stop_ec2_instances('i-0804ba3592cc35489', 'on')

