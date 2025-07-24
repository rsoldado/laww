import yaml
import logging
from pathlib import Path
from urllib.parse import urlparse
import re

# Classes for configurations
class TargetConfig:

    class TargetSettings:
        def __init__(self, 
                     interval: int = 300,
                     retry_delay: int = 60,
                     timeout: int = 10):
            self.interval = interval
            self.retry_delay = retry_delay
            self.timeout = timeout
            self._validate()
        
        def _validate(self):
            """Validate target settings parameters."""
            if not isinstance(self.interval, int) or self.interval <= 0:
                raise ValueError(f"interval must be a positive integer, got: {self.interval}")
            
            if not isinstance(self.retry_delay, int) or self.retry_delay < 0:
                raise ValueError(f"retry_delay must be a non-negative integer, got: {self.retry_delay}")
            
            if not isinstance(self.timeout, int) or self.timeout <= 0:
                raise ValueError(f"timeout must be a positive integer, got: {self.timeout}")

        def __repr__(self):
            return (
                f"TargetSettings(\n"
                f"  interval={self.interval}s,\n"
                f"  retry_delay={self.retry_delay}s,\n"
                f"  timeout={self.timeout}s\n"
                f")"
            )

    class OutputConfig:
        def __init__(self, type: str, **kwargs):
            self.type = type
            self.config = kwargs
            self._validate()

        def _validate(self):
            """Validate output configuration based on type."""
            if not self.type:
                raise ValueError("Output type cannot be empty")
            
            if self.type not in ['file', 'github']:
                raise ValueError(f"Output type must be 'file' or 'github', got: {self.type}")
            
            if self.type == 'file':
                if 'path' not in self.config:
                    raise ValueError("File output type requires 'path' parameter")
                if not self.config['path']:
                    raise ValueError("File path cannot be empty")
            
            elif self.type == 'github':
                required_params = ['repository', 'path', 'token_env']
                for param in required_params:
                    if param not in self.config:
                        raise ValueError(f"GitHub output type requires '{param}' parameter")
                    if not self.config[param]:
                        raise ValueError(f"GitHub {param} cannot be empty")
                
                # Validate repository format (should be username/repo)
                repo_pattern = r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$'
                if not re.match(repo_pattern, self.config['repository']):
                    raise ValueError(f"Invalid repository format: {self.config['repository']}. Expected format: username/repository")

        def __repr__(self):
            config_str = ",\n".join([f"    {k}='{v}'" for k, v in self.config.items()])
            return (
                f"OutputConfig(\n"
                f"  type='{self.type}',\n"
                f"{config_str}\n"
                f")"
            )

    def __init__(self, name: str, url: str, output, settings: dict = {}, type: str = "web"):
        self.name = name
        self.url = url
        self.type = type
        
        # Handle both single output (dict) and multiple outputs (list)
        if isinstance(output, dict):
            # Single output - convert to list for consistency
            self.outputs = [self.OutputConfig(output['type'], **{k: v for k, v in output.items() if k != 'type'})]
        elif isinstance(output, list):
            # Multiple outputs
            self.outputs = []
            for out in output:
                self.outputs.append(self.OutputConfig(out['type'], **{k: v for k, v in out.items() if k != 'type'}))
        else:
            raise ValueError("Output must be a dict or list of dicts")
            
        # Keep backward compatibility
        self.output = self.outputs[0] if self.outputs else None
            
        self.settings = self.TargetSettings(**settings)
        self._validate()

    def _validate(self):
        """Validate target configuration."""
        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("Target name cannot be empty")
        
        # Validate type
        if self.type not in ['web', 'zeronet']:
            raise ValueError(f"Target type must be 'web' or 'zeronet', got: {self.type}")
        
        # Validate URL
        if not self.url or not self.url.strip():
            raise ValueError("Target URL cannot be empty")
        
        parsed_url = urlparse(self.url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid URL format: {self.url}")
        
        if parsed_url.scheme not in ['http', 'https']:
            raise ValueError(f"URL must use http or https protocol, got: {parsed_url.scheme}")

    def __repr__(self):
        outputs_str = ",\n    ".join([repr(output).replace('\n', '\n    ') for output in self.outputs])
        return (
            f"TargetConfig(\n"
            f"  name='{self.name}',\n"
            f"  url='{self.url}',\n"
            f"  type='{self.type}',\n"
            f"  outputs=[\n    {outputs_str}\n  ],\n"
            f"  settings={repr(self.settings).replace(chr(10), chr(10) + '  ')}\n"
            f")"
        )

# Loading function
def load_config(config_file: str):

    logging.debug(f"Loading configuration from {config_file}...")

    # Verifies that exists
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load the config file
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML syntax in config file: {e}")
    
    # Load targets
    targets = config_data.get('targets', [])
    if not targets:
        raise ValueError("At least one target must be defined in the configuration")

    # Create configuration objects
    configs = []
    for target in targets:
        try:
            tc = TargetConfig(target['name'], 
                              target['url'], 
                              target['output'], 
                              target.get('settings', {}),
                              target.get('type', 'web'))
            configs.append(tc)
        except:
            logging.warning(f"Invalid target configuration: {target}")

    if not configs:
        raise ValueError("No valid targets found in configuration")

    logging.debug(f"Configuration loaded successfully.")
    logging.debug(f"{len(configs)} target(s) found.")
    return configs