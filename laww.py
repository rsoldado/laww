#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import hashlib
import base64
import logging
import argparse
from dotenv import load_dotenv

"""
* Automatic list updater
    This script will fetch a list from a given LIST_URL, compare it with a local and remote copy,
    updating both if there are any changes.
"""

# Configurate logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():

    parser = argparse.ArgumentParser(description='Automatic list updater')
    parser.add_argument('--env', type=str, help='Path to the environment file')
    args = parser.parse_args()

    # Load environment variables
    if args.env:
        load_dotenv(args.env)
    LIST_URL = os.getenv('LIST_URL')
    GITHUB_USER = os.getenv('GITHUB_USER')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    GITHUB_FILE = os.getenv('GITHUB_FILE')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

    if not all([LIST_URL, GITHUB_USER, GITHUB_REPO, GITHUB_FILE, GITHUB_TOKEN]):
        logging.error('Missing environment variables')
        return
    
    # Fetch list from source
    try:
        response = requests.get(LIST_URL)
        response.raise_for_status()
        list = response.text
    except:
        logging.error('List source unavailable')
        return
    
    # Check if there are local changes
    try:
        with open('list.m3u', 'r') as f:
            local_list = f.read()
    except:
        local_list = ''
    
    # Check for changes
    h1 = hashlib.sha256(list.encode('utf-8')).hexdigest()
    h2 = hashlib.sha256(local_list.encode('utf-8')).hexdigest()
    if h1 == h2:
        logging.info('List is already updated')
        return
    
    # Fetch remote list
    remote_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    remote_headers = {
        'Authorization': f"Bearer {GITHUB_TOKEN}",
        'Accept': 'application/vnd.github.v3+json'
    }
    try:
        response = requests.get(remote_url, headers=remote_headers)
        response.raise_for_status()
        json = response.json()
        sha = json['sha']
        remote_list = base64.b64decode(json['content']).decode('utf-8')

    except:
        logging.warning('Remote list does not exist')
        remote_list = ''
        sha = None

    # Check for changes
    h3 = hashlib.sha256(remote_list.encode('utf-8')).hexdigest()
    if h1 == h3:
        logging.info('List is already updated remotely')
        # Save locally
        with open('list.m3u', 'w') as f:
            f.write(list)
        return
    
    # Update list
    data = {
        'message': f"List updated",
        'content': base64.b64encode(list.encode('utf-8')).decode('utf-8'),
        "branch": "main"
    }
    if sha:
        data['sha'] = sha
    try:
        response = requests.put(remote_url, headers=remote_headers, json=data)
        response.raise_for_status()
    except:
        logging.error('Unable to update remote list')
        return
    
    # Save locally
    with open('list.m3u', 'w') as f:
        f.write(list)

    logging.info('List updated')


if __name__ == '__main__':
    main()