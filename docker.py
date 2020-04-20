import sys
import os
import json
import argparse
import subprocess

docker_image_name = 'nnaydenovdocker/gmail-cli-tool'

def execute_shell(cmd):


def get_version():
    try:
        with open('VERSION', 'r') as vf:
            version = vf.strip()
        
        return version

    except Exception as e:
        raise(f'Error, {e}')


def main(config_file, dry_run):
    with open(config_file, 'r') as f:
         docker_creds = json.load(f)

    print(f'Login to Docker Registry {docker_registry_url}')
    execute_shell(f'docker login -u "{docker_creds['username']}" -p "{docker_creds['password']}" {docker_creds['docker_registry']}')
    print(f'Login to Docker Registry {docker_registry_url}')
    docker_image_version = get_version()
    execute_shell(f'docker build -t {docker_image_name}:{docker_image_version} .')
    







if __name__ == '__main__':
    parser = argparse.ArgumentParser()   
    parser.add_argument('--config_file', required=False, default='C:\\Users\\Nikola Naydenov\\Desktop\\AWS\\.config\\.docker_config.json', 
                        help='Docker Registry config file path')
    parser.add_argument('--dry_run', required=False, default=False, help='Dry Run option')
    args = parser.parse_args()

    main(args.config_file, args.docker_registry_url, args.dry_run)