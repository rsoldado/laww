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

    def __init__(self, url: str, settings: TargetConfig.TargetSettings):
        self.url = url
        self.timeout = settings.timeout

        # Suppress logging from requests and urllib3
        logging.getLogger("requests").setLevel(logging.CRITICAL)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)

        
    def fetch(self) -> Optional[Dict[str, Any]]:
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

    def _get_sha(self, content: bytes) -> str:
        sha = hashlib.sha256()
        sha.update(content)
        return sha.hexdigest()