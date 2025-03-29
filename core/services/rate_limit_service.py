import time
from collections import deque
from ipaddress import ip_network, ip_address
import threading
import logging

logger = logging.getLogger(__name__)

class RateLimitService:
    def __init__(self):
        self.hourly_limit = 10
        self.daily_limit = 30
        self.hourly_window = 3600  # 1 hour in seconds
        self.daily_window = 86400  # 24 hours in seconds
        self.whitelist = [ip_network('205.193.0.0/16')]
        self.usage = {}
        self._lock = threading.Lock()

    def is_whitelisted(self, ip: str) -> bool:
        """
        Check if the given IP address is in any of the whitelisted CIDRs.

        :param ip: The IPv4 or IPv6 address to check.
        :return: True if the IP is whitelisted, False otherwise.
        """
        try:
            ip_addr = ip_address(ip)
            return any(ip_addr in network for network in self.whitelist)
        except ValueError as e:
            logger.error(f"Invalid IP format: {ip}")
            return False

    def increment(self, ip: str) -> bool:
        """
        Increment the rate limit count for the given IP address and check if it exceeds the limits.

        :param ip: The IPv4 or IPv6 address to track.
        :return: True if the operation is allowed (not exceeding any limits), False otherwise.
        """
        with self._lock:
            if self.is_whitelisted(ip):
                return True

            current_time = time.time()
            if ip not in self.usage:
                self.usage[ip] = {'hourly': deque(), 'daily': deque()}

            self.usage[ip]['hourly'].append(current_time)
            self.usage[ip]['daily'].append(current_time)

            # Remove timestamps outside the rolling windows
            while self.usage[ip]['hourly'] and self.usage[ip]['hourly'][0] < current_time - self.hourly_window:
                self.usage[ip]['hourly'].popleft()
            while self.usage[ip]['daily'] and self.usage[ip]['daily'][0] < current_time - self.daily_window:
                self.usage[ip]['daily'].popleft()

            if not self.check_limits(ip):
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return False
            else:
                logger.info(f"Increment successful for IP: {ip}")
                return True

    def check_limits(self, ip: str) -> bool:
        """
        Check if the given IP address exceeds the rate limits.

        :param ip: The IPv4 or IPv6 address to track.
        :return: True if the operation is allowed (not exceeding any limits), False otherwise.
        """
        with self._lock:
            if self.is_whitelisted(ip):
                return True

            hourly_usage = len(self.usage[ip]['hourly'])
            daily_usage = len(self.usage[ip]['daily'])

            if hourly_usage > self.hourly_limit or daily_usage > self.daily_limit:
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return False
            else:
                logger.info(f"IP: {ip} usage is within limits")
                return True

    def get_usage(self, ip: str) -> dict:
        """
        Get the current hourly and daily rate limit usage for the given IP address.

        :param ip: The IPv4 or IPv6 address to track.
        :return: A dictionary containing 'hourly' and 'daily' usage count.
        """
        with self._lock:
            if ip not in self.usage:
                return {'hourly': 0, 'daily': 0}

            hourly_usage = len(self.usage[ip]['hourly'])
            daily_usage = len(self.usage[ip]['daily'])

            logger.debug(f"IP: {ip} - Hourly usage: {hourly_usage}, Daily usage: {daily_usage}")
            return {'hourly': hourly_usage, 'daily': daily_usage}

    def add_whitelist_cidr(self, cidr: str) -> None:
        """
        Add a new whitelisted CIDR block.

        :param cidr: The CIDR (e.g., 192.0.2.0/24) to be added.
        """
        with self._lock:
            try:
                network = ip_network(cidr)
                if network not in self.whitelist:
                    self.whitelist.append(network)
                    logger.info(f"Whitelisted CIDR: {cidr}")
            except ValueError as e:
                logger.error(f"Invalid CIDR format: {cidr}. Error: {e}")
