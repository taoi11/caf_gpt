import os
import json
import logging
import time
import requests
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class CostTrackerService:
    """
    Tracks the cost of OpenRouter API generations by fetching cost details
    asynchronously using threading.

    Fetches cost details using the generation ID after a delay and appends
    the cost data to a JSON Lines file.
    """

    def __init__(self):
        """
        Initializes the service with API key and data storage path.
        Ensures the data directory exists.
        """
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY environment variable not set. Cost tracking disabled.")
        # Use pathlib for robust path handling
        self.data_dir = Path("./data")
        self.cost_file_path = self.data_dir / "cost.json"  # Use .json for single total
        self._ensure_data_dir_exists()
        self._initialize_cost_file()  # Initialize the cost file with proper structure
        self.api_url_base = "https://openrouter.ai/api/v1/generation"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://caf-gpt.com",  # Optional but recommended
            "X-Title": "CAF-GPT"  # Optional but recommended
        }
        # Lock for thread-safe file writing
        self._file_lock = threading.Lock()

    def _ensure_data_dir_exists(self):
        """Creates the data directory if it doesn't exist."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured data directory exists: {self.data_dir}")
        except OSError as e:
            logger.error(f"Failed to create data directory {self.data_dir}: {e}")

    def _fetch_and_save_cost(self, gen_id: str):
        """
        Internal method to fetch, process, and save cost data.
        Designed to be run in a separate thread.

        Args:
            gen_id: The generation ID from the OpenRouter completion response.
        """
        if not self.api_key:
            # Already logged in __init__, but good to double-check
            logger.warning("Skipping cost tracking: API key not configured.")
            return

        try:
            # 0.5 second delay
            time.sleep(0.5)

            url = f"{self.api_url_base}?id={gen_id}"
            logger.info(f"Fetching cost data for gen_id: {gen_id} in background thread.")

            response = requests.get(url, headers=self.headers, timeout=30)  # 30 second timeout

            if response.status_code == 200:
                response_data = response.json()
                cost_data = response_data.get('data')

                if cost_data:
                    new_usage = cost_data.get('usage')
                    if isinstance(new_usage, (float, int)):
                        self._update_total_usage(float(new_usage))
                        logger.info(f"Updated total usage for gen_id: {gen_id} with value: {new_usage}")
                    else:
                        logger.warning(f"Invalid 'usage' field in cost data for gen_id: {gen_id}. Found: {new_usage}")
                else:
                    logger.warning(f"No 'data' field found in cost response for gen_id: {gen_id}. Response: {response_data}")

            else:
                logger.error(f"Failed to fetch cost data for gen_id: {gen_id}. Status: {response.status_code}, Response: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching cost data for gen_id {gen_id}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response for cost data gen_id {gen_id}: {e}")
        except Exception as e:
            # Catching broader exceptions that might occur in the thread
            logger.error(f"Unexpected error tracking cost for gen_id {gen_id} in background thread: {e}", exc_info=True)

    def _initialize_cost_file(self):
        """Ensures the cost JSON file exists and contains the basic structure."""
        try:
            with self._file_lock:
                if not self.cost_file_path.exists():
                    with open(self.cost_file_path, 'w', encoding='utf-8') as f:
                        json.dump({"total_usage": 0.0}, f, indent=4)
                    logger.info(f"Initialized cost file: {self.cost_file_path}")
        except IOError as e:
            logger.error(f"Failed to initialize cost file {self.cost_file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error initializing cost file: {e}", exc_info=True)

    def _update_total_usage(self, new_usage: float):
        """Reads the current total usage, adds the new usage, and writes it back."""
        try:
            with self._file_lock:
                current_total = 0.0
                try:
                    if self.cost_file_path.exists() and self.cost_file_path.stat().st_size > 0:
                        with open(self.cost_file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            current_total = data.get("total_usage", 0.0)
                            if not isinstance(current_total, (float, int)):
                                logger.warning(f"Invalid 'total_usage' format ({current_total}), resetting to 0.0")
                                current_total = 0.0
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error reading cost file, resetting total: {e}")
                    current_total = 0.0

                updated_total = current_total + new_usage

                with open(self.cost_file_path, 'w', encoding='utf-8') as f:
                    json.dump({"total_usage": updated_total}, f, indent=4)
        except Exception as e:
            logger.error(f"Unexpected error updating total usage: {e}", exc_info=True)

    def get_total_usage(self) -> float:
        """
        Safely reads and returns the current total usage from the cost file.

        Returns:
            float: The current total usage cost in USD
        """
        try:
            with self._file_lock:
                if not self.cost_file_path.exists():
                    return 0.0

                with open(self.cost_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total = data.get("total_usage", 0.0)
                    if not isinstance(total, (float, int)):
                        logger.warning(f"Invalid 'total_usage' format ({total}), returning 0.0")
                        return 0.0
                    return float(total)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading cost file: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Unexpected error getting total usage: {e}", exc_info=True)
            return 0.0

    def track_cost(self, gen_id: str):
        """
        Starts the cost tracking process for a given generation ID in a background thread.

        This method returns immediately.

        Args:
            gen_id: The generation ID from the OpenRouter completion response.
        """
        if not gen_id or not isinstance(gen_id, str):
            logger.warning(f"Skipping cost tracking: Invalid gen_id received: {gen_id}")
            return

        if not self.api_key:
            logger.warning("Skipping cost tracking thread start: API key not configured.")
            return

        logger.debug(f"Scheduling cost tracking for gen_id: {gen_id}")
        # Create and start a daemon thread to run the fetching and saving
        # Daemon threads exit when the main program exits
        thread = threading.Thread(target=self._fetch_and_save_cost, args=(gen_id,), daemon=True)
        thread.start()
