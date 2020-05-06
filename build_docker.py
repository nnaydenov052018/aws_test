import sys
import os
import json, yaml
import argparse

docker_image_name = 'nnaydenovdocker/gmail-cli-tool'

def get_root_path():
    return os.path.dirname(os.path.abspath(__file__))

def execute_shell(cmd):
    try:
        exit_code = os.system(cmd)
        return exit_code
  
    except Exception as e:
        raise(f'Error executing command {cmd}, {e}')

def get_version():
    try:
        with open(os.path.join(get_root_path(), 'VERSION'), 'r') as vf:
            version = vf.read().strip()
        
        return version

    except Exception as e:
        raise(f'Error, {e}')

def generate_docker_compose(version):
    try:
        with open(os.path.join(get_root_path(), 'docker-compose', 'docker-compose.yml_tpl'), 'r') as f:
            docker_compose_dt = yaml.load(f, Loader=yaml.FullLoader)
        
        docker_compose_dt['services']['gmail-cli']['image'] = f"{docker_image_name}:{version}"

        with open(os.path.join(get_root_path(), 'docker-compose', 'docker-compose.yml'), 'w') as f:
            yaml.dump(docker_compose_dt, f, default_flow_style=False, sort_keys=False)
    
    except Exception as e:
        raise(f'Error, {e}')


def main(config_file):
    with open(config_file, 'r') as f:
         docker_creds = json.load(f)

    print(f"\n ========== Login to Docker Registry {docker_creds['docker_registry']} ========== \n")
    execute_shell(f"docker login -u {docker_creds['username']} -p {docker_creds['password']} {docker_creds['docker_registry']}")
    
    print(f'\n ========== Building docker image from Dockerfile ========== \n')
    docker_image_version = get_version()
    execute_shell(f"docker build -t {docker_image_name}:{docker_image_version} .")
    
    print(f'\n ========== Tag latest docker image ========== \n')
    execute_shell(f"docker tag {docker_image_name}:{docker_image_version} {docker_image_name}:latest")
    
    # Check if image version already exist in docker registry
    image_exist = execute_shell(f"docker pull {docker_image_name}:{docker_image_version}")
    if image_exist:
        print(f"\n ========== Image {docker_image_name}:{docker_image_version} do not exist in registry. Uploading ========== \n")
        execute_shell(f"docker push {docker_image_name}:{docker_image_version}")
    
    print(f"\n ========== Push latest image {docker_image_name}:latest ========== \n")
    execute_shell(f"docker push {docker_image_name}:latest")

    print(f"\n ========== Logout docker registry ========== \n")
    execute_shell(f"docker logout")

    print(f"\n ========== Generate docker-compose.yml ========== \n")
    generate_docker_compose(docker_image_version)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', required=False, default='C:\\Users\\Nikola Naydenov\\Desktop\\AWS\\.config\\.docker_config.json', 
                        help='Docker Registry config file path')
    args = parser.parse_args()

    main(args.config_file)
