import logging
import requests
import hashlib
from typing import Optional, Dict, Any

from .config import TargetConfig


class FileFetcher:

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'
    }

    def __init__(self, url: str, settings: TargetConfig.TargetSettings, target_type: str):
        self.url = url
        self.timeout = settings.timeout
        self.target_type = target_type

        # Assign correspondent fetch function
        if target_type == "web":
            self.fetch = self.fetch_web
        elif target_type == "zeronet":
            self.fetch = self.fetch_zeronet
            # Also extract the main site address for ZeroNet
            url_parts = self.url.split('/')
            if len(url_parts) < 5:
                raise ValueError(f"Invalid ZeroNet URL format: {self.url}")
            base_url = '/'.join(url_parts[:4])  # http://127.0.0.1:43110
            site_address = url_parts[4]
            self.main_url = f"{base_url}/{site_address}/"
        else:
            raise ValueError(f"Unsupported target type: {target_type}")

        # Suppress logging from requests and urllib3
        logging.getLogger("requests").setLevel(logging.CRITICAL)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)

        
    def fetch_web(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()  # Raise exception for HTTP error codes
            return {
                'file': response.content,
                'sha': self._get_sha(response.content)
            }

        except requests.exceptions.Timeout:
            logging.debug(f"Timeout fetching {self.url}")
            raise
            
        except requests.exceptions.ConnectionError:
            logging.debug(f"Connection error fetching {self.url}")
            raise
            
        except requests.exceptions.HTTPError as e:
            logging.debug(f"HTTP error fetching {self.url}: {e}")
            raise
            
        except Exception as e:
            logging.debug(f"Unexpected error fetching {self.url}: {e}")
            raise

    def fetch_zeronet(self) -> Optional[Dict[str, Any]]:
        try:
            # First load the main site
            main_response = requests.get(self.main_url, headers=self.headers, timeout=self.timeout)
            main_response.raise_for_status()
            # Then get the specific file
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return {
                'file': response.content,
                'sha': self._get_sha(response.content)
            }

        except requests.exceptions.Timeout:
            logging.debug(f"Timeout fetching ZeroNet URL {self.url}")
            raise
            
        except requests.exceptions.ConnectionError:
            logging.debug(f"Connection error fetching ZeroNet URL {self.url}")
            raise
            
        except requests.exceptions.HTTPError as e:
            logging.debug(f"HTTP error fetching ZeroNet URL {self.url}: {e}")
            raise
            
        except ValueError as e:
            logging.debug(f"Invalid ZeroNet URL {self.url}: {e}")
            raise
            
        except Exception as e:
            logging.debug(f"Unexpected error fetching ZeroNet URL {self.url}: {e}")
            raise

    def _get_sha(self, content: bytes) -> str:
        sha = hashlib.sha256()
        sha.update(content)
        return sha.hexdigest()