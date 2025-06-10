import os
import logging
import time
import requests
import threading
from django.db import connection, OperationalError, ProgrammingError

logger = logging.getLogger(__name__)


class CostTrackerService:
    """
    Tracks the cost of OpenRouter API generations by fetching cost details
    asynchronously using threading.

    Fetches cost details using the generation ID after a delay and updates
    the cost data in the database.
    """

    def __init__(self):
        """
        Initializes the service with API key.
        Checks if the cost_tracker table exists.
        """
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY environment variable not set. Cost tracking disabled.")
        
        self._lock = threading.Lock()
        self._check_table_exists()
        
        self.api_url_base = "https://openrouter.ai/api/v1/generation"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://caf-gpt.com",  # Optional but recommended
            "X-Title": "CAF-GPT"  # Optional but recommended
        }

    def _check_table_exists(self):
        """Checks if the cost_tracker table exists in the database."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'cost_tracker'
                    )
                """)
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    logger.error("The cost_tracker table does not exist in the database. Cost tracking may not work properly.")
                else:
                    logger.info("Cost tracker table exists in the database.")
        except (OperationalError, ProgrammingError) as e:
            logger.error(f"Database error when checking for cost_tracker table: {e}")
        except Exception as e:
            logger.error(f"Unexpected error checking cost_tracker table: {e}", exc_info=True)

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
        except Exception as e:
            # Catching broader exceptions that might occur in the thread
            logger.error(f"Unexpected error tracking cost for gen_id {gen_id} in background thread: {e}", exc_info=True)

    def _update_total_usage(self, new_usage: float):
        """Updates the total usage in the database by adding the new usage."""
        try:
            # Import here to avoid circular imports
            from core.models import CostTracker
            
            with self._lock:
                try:
                    from django.db import transaction
                    # Wrap the update in a transaction to ensure atomicity
                    with transaction.atomic():
                        # Get or create the singleton record
                        cost_tracker = CostTracker.get_or_create_singleton()
                        
                        # Update the total usage
                        cost_tracker.total_usage += new_usage
                        cost_tracker.save()
                    
                except OperationalError as e:
                    logger.error(f"Database operational error updating total usage: {e}")
                except ProgrammingError as e:
                    logger.error(f"Database programming error updating total usage: {e}")
                except Exception as e:
                    logger.error(f"Database error updating total usage: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating total usage: {e}", exc_info=True)

    def get_total_usage(self) -> float:
        """
        Safely reads and returns the current total usage from the database.

        Returns:
            float: The current total usage cost in USD
        """
        try:
            # Import here to avoid circular imports
            from core.models import CostTracker
            
            with self._lock:
                try:
                    # Get or create the singleton record
                    cost_tracker = CostTracker.get_or_create_singleton()
                    return float(cost_tracker.total_usage)
                except OperationalError as e:
                    logger.error(f"Database operational error getting total usage: {e}")
                except ProgrammingError as e:
                    logger.error(f"Database programming error getting total usage: {e}")
                except Exception as e:
                    logger.error(f"Database error getting total usage: {e}")
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
