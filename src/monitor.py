import threading
import time
import logging
import signal
import sys
from typing import Optional, Dict

from .config import TargetConfig
from .fetcher import FileFetcher
from .outputs import OutputManager


# Single File monitor class
class FileMonitor:
    
    def __init__(self, config: TargetConfig):
        self.config = config
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.running = False
        
        # Initialize fetcher and output manager
        self.fetcher = FileFetcher(self.config.url, self.config.settings)
        self.output = OutputManager(self.config.outputs)
        self.last_content = None  # Store last fetched content for comparison

        logging.debug(f"Monitoring target [{self.config.name}].")

    def start(self):
        # Check that is stopped
        if self.running:
            return
        # Remove stop signal from thread
        self.stop_event.clear()
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        # Check that is running
        if not self.running:
            return    
        # Send stop signal to thread
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        self.running = False
        
    def is_running(self) -> bool:
        # Check if monitor is running
        return self.running and self.thread and self.thread.is_alive()
        
    def _monitor_loop(self):
        time.sleep(3) # Initial delay to allow setup
        # Main monitoring loop with auto-restart on failure
        while not self.stop_event.is_set():
            try:
                self._check_file()
            except Exception as e:
                # Wait retry time or stop signal
                if self.stop_event.wait(self.config.settings.retry_delay):
                    break  # Only break if stop was requested during wait
                continue
            # Wait for interval or stop signal
            if self.stop_event.wait(self.config.settings.interval):
                break  # Only break if stop was explicitly requested
        
    def _check_file(self):

        # Fetch file
        try:
            res = self.fetcher.fetch()
            file = res.get('file')
            sha = res.get('sha')
        except Exception as e:
            logging.warning(f"⚠️  Target '{self.config.name}' is not available.")
            raise e  # Re-raise to enable retry logic
        
        # Check if there are changes
        if self.last_content == sha:
            logging.debug(f"No changes in target '{self.config.name}'")
            return

        # Process the outputs
        try:
            self.output.process_output(file)
            self.last_content = sha  # Update last content after successful fetch
            logging.info(f"✅  Target '{self.config.name}' updated successfully.")
        except Exception as e:
            logging.error(f"❌  Error updating target '{self.config.name}': {e}")
            raise e  # Re-raise to enable retry logic


# Collection of file monitors
class FileMonitorManager:
    
    def __init__(self):
        self.monitors: Dict[str, FileMonitor] = {}
        self.running = False
        
        # Handle shutdown signals
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def add_monitor(self, config: TargetConfig) -> FileMonitor:
        # Check if monitor already exists and replace it
        if config.name in self.monitors:
            self.remove_monitor(config.name)
        # Create and add new monitor
        monitor = FileMonitor(config)
        self.monitors[config.name] = monitor
        return monitor
        
    def remove_monitor(self, name: str) -> bool:
        # Check if monitor exists
        if name not in self.monitors:
            return False
        
        # Stop and remove the monitor
        monitor = self.monitors[name]
        if monitor.is_running():
            monitor.stop()
        del self.monitors[name]
        return True
        
    def start_all(self):
        if self.running:
            return
        # Start all monitors
        self.running = True
        for name, monitor in self.monitors.items():
            monitor.start()
        logging.info(f"Starting the file monitors.")

    def stop_all(self):
        # Send stop event to all monitors
        for monitor in self.monitors.values():
            monitor.stop()
        self.running = False
        logging.info(f"Stopping the file monitors.")

    def get_status(self) -> Dict[str, bool]:
        # Get status of all monitors
        return {name: monitor.is_running() for name, monitor in self.monitors.items()}
        
    def wait_for_completion(self):
        # Wait for monitors to run until interrupted with health checking
        if not self.running:
            return
            
        logging.info("Press Ctrl+C to stop...")
        try:
            while self.running:
                time.sleep(10)  # Check every 10 seconds
                self._check_monitor_health()
        except KeyboardInterrupt:
            logging.info("Stopping...")
            
    def _check_monitor_health(self):
        # Check monitor health and restart if needed
        for name, monitor in self.monitors.items():
            if not monitor.is_running() and self.running:
                logging.warning(f"Monitor '{name}' has stopped unexpectedly, restarting...")
                try:
                    # Reset the monitor state
                    monitor.running = False
                    monitor.stop_event.clear()
                    # Start it again
                    monitor.start()
                    logging.debug(f"Successfully restarted monitor '{name}'")
                except Exception as e:
                    logging.error(f"Failed to restart monitor '{name}': {e}")
                    # Try to recreate the monitor completely
                    try:
                        logging.debug(f"Attempting to recreate monitor '{name}'...")
                        old_config = monitor.config
                        del self.monitors[name]
                        new_monitor = FileMonitor(old_config)
                        self.monitors[name] = new_monitor
                        new_monitor.start()
                        logging.debug(f"Successfully recreated and started monitor '{name}'")
                    except Exception as e2:
                        logging.error(f"Failed to recreate monitor '{name}': {e2}")
            
    def _signal_handler(self, signum, frame):
        print()
        self.stop_all()
        sys.exit(0)