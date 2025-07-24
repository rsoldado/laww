#!/usr/bin/env python3
"""
LAWW - File Monitor Application
A simple file monitoring tool with configurable targets and outputs.
"""

import sys
import logging
import argparse
from time import sleep
from dotenv import load_dotenv

from src.config import load_config
from src.monitor import FileMonitorManager


def main():
    # Load environment variables
    load_dotenv()

    # Parse arguments
    parser = argparse.ArgumentParser(description="LAWW - File Monitor Application")
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Config file path (default: config.yaml)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    args = parser.parse_args()
    
    # Create logger
    loglevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%d/%m/%y %H:%M:%S",
    )
    logging.info("LAWW - File Monitor Application - v1.2")

    # Load configuration
    try :
        configs = load_config(args.config)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        sleep(10)
        logging.info("Shutting down...")
        return 1

    # Start file monitors
    monitor_manager = FileMonitorManager()
    # Add all configured targets to the monitor manager
    for config in configs:
        monitor_manager.add_monitor(config)
    
    # Start all monitors and wait for completion
    try:
        # Start all monitors and wait until completion
        monitor_manager.start_all()        
        monitor_manager.wait_for_completion()
    except Exception as e:
        logging.error(f"Error running monitors: {e}")
        return 1
    finally:
        logging.info("Shutting down...")


if __name__ == "__main__":
    sys.exit(main())
