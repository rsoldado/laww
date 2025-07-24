import logging
import os
import base64
import requests
from pathlib import Path

from .config import TargetConfig


class FileSaver:    
    def __init__(self, path: str):
        # Check the path and create directory if it doesn't exist
        self.path = Path('./downloads/' + path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def process(self, file: str):
        # Write binary content to file
        with open(self.path, 'wb') as f:
            f.write(file)
        logging.debug(f"File saved in {self.path}")

class GitHubUploader:    
    def __init__(self, repository: str, path: str, token: str):
        # Check that all required parameters are provided
        if not all([repository, path, token]):
            raise ValueError("GitHub uploader requires repository, path, and token parameters")
        # GitHub API elements
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        self.url = f"https://api.github.com/repos/{repository}/contents/{path}"

    def process(self, file: str):
        # Encode file for GitHub API (base64)
        enc_file = base64.b64encode(file).decode('utf-8')
        # Prepare the commit data
        commit_data = {
            'message': f'Updated with LAWW',
            'content': enc_file
        }

        # Get the existing file
        res = requests.get(self.url, headers=self.headers)
        # If file exists, add its SHA for update
        if res.status_code == 200:
            existing_file = res.json()
            commit_data['sha'] = existing_file['sha']
        
        # Upload/update file
        res = requests.put(self.url, json=commit_data, headers=self.headers)
        if res.status_code not in [200, 201]:
            raise Exception(f"GitHub upload failed: {res.status_code} - {res.text}")
        logging.debug(f"Successfully uploaded to GitHub: {self.url}")


class OutputManager:    
    def __init__(self, outputs: list[TargetConfig.OutputConfig]):
        # Create objects according to outputs
        self.outputs = []
        for output_config in outputs:
            try:
                if output_config.type == 'file':
                    self.outputs.append(FileSaver(output_config.config['path']))
                elif output_config.type == 'github':
                    token = os.getenv(output_config.config['token_env'])
                    self.outputs.append(GitHubUploader(output_config.config['repository'], output_config.config['path'], token))
            except Exception as e:
                logging.warning(f"Failed to initialize output '{output_config.type}': {e}")
                continue
        # Check that there are some valid output
        if not self.outputs:
            raise ValueError("No valid outputs configured in TargetConfig")

    def process_output(self, file: str):
        # Process each output
        for _, output in enumerate(self.outputs):
            output.process(file) 
        # If it fails in any of them, the File Monitor will manage it.
