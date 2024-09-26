import subprocess
import platform
import os
import json

def get_conda_env_name():
    try:
        # Get the directory of the current environment from CONDA_PREFIX or CONDA_DEFAULT_ENV
        conda_prefix = os.environ.get("CONDA_PREFIX")
        conda_default_env = os.environ.get("CONDA_DEFAULT_ENV")
        
        if conda_prefix:
            # Return the basename of the conda_prefix path
            return os.path.basename(conda_prefix)
        elif conda_default_env:
            return conda_default_env
        else:
            print("No active Conda environment detected.")
            return None
    except Exception as e:
        print(f"Error detecting the conda environment: {e}")
        return None

def open_new_terminal(command, work_dir, conda_env_name):
    if conda_env_name:
        if platform.system() == 'Windows':
            conda_activate = f'conda activate {conda_env_name}'
            full_command = f'cd /d {work_dir} && {conda_activate} && {command}'
            subprocess.Popen(['start', 'cmd', '/k', full_command], shell=True)
        elif platform.system() == 'Darwin':  # macOS
            conda_activate = f'conda activate {conda_env_name}'
            full_command = f'cd {work_dir} && {conda_activate} && {command}'
            subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "{full_command}"'])
        else:  # assume Linux
            conda_activate = f'source ~/mambaforge/etc/profile.d/conda.sh && conda activate {conda_env_name}'
            full_command = f'cd {work_dir} && {conda_activate} && {command}'
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', full_command], shell=True)
    else:
        print("No active conda environment found. Running the commands without conda activation.")
        if platform.system() == 'Windows':
            full_command = f'cd /d {work_dir} && {command}'
            subprocess.Popen(['start', 'cmd', '/k', full_command], shell=True)
        elif platform.system() == 'Darwin':  # macOS
            full_command = f'cd {work_dir} && {command}'
            subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "{full_command}"'])
        else:  # assume Linux
            full_command = f'cd {work_dir} && {command}'
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', full_command], shell=True)

if __name__ == '__main__':
    # Get the current working directory where this script is located
    work_dir = os.path.dirname(os.path.realpath(__file__))

    # Get active conda environment name
    conda_env_name = get_conda_env_name()
    
    if conda_env_name:
        print(f"Detected active conda environment: {conda_env_name}")
    else:
        print("No active conda environment detected.")
    
    # Command to be run in the first terminal window
    open_new_terminal('ollama run gemma:7b', work_dir, conda_env_name)
    
    # Command to be run in the second terminal window
    open_new_terminal('python app.py', work_dir, conda_env_name)
    
    # Command to be run in the third terminal window
    open_new_terminal('python -m http.server', work_dir, conda_env_name)

    print("All commands have been executed. The app should be running at http://localhost:8000.")