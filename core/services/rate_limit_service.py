import time
from collections import deque
from ipaddress import ip_network, ip_address


class RateLimitService:
    """
    Implements IP-based rate limiting with rolling time windows.

    Manages hourly and daily request limits, supports IP whitelisting,
    and efficiently tracks usage through timestamp deques.
    """

    def __init__(self):
        """
        Initializes the RateLimitService with default limits, windows, and whitelist.
        """
        self.hourly_limit = 10
        self.daily_limit = 30
        self.hourly_window = 3600  # 1 hour in seconds
        self.daily_window = 86400  # 24 hours in seconds
        self.whitelist = [
            ip_network('205.193.0.0/16'),
            # ip_network('127.0.0.1/32') # Whitelist localhost for development (Temporarily commented out for testing)
        ]
        self.usage = {}  # Dictionary to store usage data per IP: {'ip': {'hourly': deque(), 'daily': deque()}}

    def is_whitelisted(self, ip):
        """
        Determines if an IP address is in any whitelisted network.
        """
        ip_addr = ip_address(ip)
        return any(ip_addr in network for network in self.whitelist)

    def increment(self, ip):
        """
        Registers an IP access attempt and evaluates limit compliance.

        For whitelisted IPs, returns True without tracking.
        Otherwise, adds current timestamp to tracking queues,
        prunes expired entries, and verifies limit status.
        """
        # Whitelisted IPs are always allowed and not tracked
        if self.is_whitelisted(ip):
            return True

        current_time = time.time()
        # Initialize usage tracking for a new IP
        if ip not in self.usage:
            self.usage[ip] = {'hourly': deque(), 'daily': deque()}
        # Record the current access time
        self.usage[ip]['hourly'].append(current_time)
        self.usage[ip]['daily'].append(current_time)
        # Remove timestamps older than the hourly window from the left of the deque
        while self.usage[ip]['hourly'] and self.usage[ip]['hourly'][0] < current_time - self.hourly_window:
            self.usage[ip]['hourly'].popleft()
        # Remove timestamps older than the daily window from the left of the deque
        while self.usage[ip]['daily'] and self.usage[ip]['daily'][0] < current_time - self.daily_window:
            self.usage[ip]['daily'].popleft()
        # Check if the current usage exceeds limits after recording the new access
        return self.check_limits(ip)

    def check_limits(self, ip):
        """
        Verifies if an IP's current usage is within defined limits.
        Evaluates existing usage without incrementing counters.
        """
        # Whitelisted IPs are always considered within limits
        if self.is_whitelisted(ip):
            return True

        # If IP is not tracked yet (first request), it's implicitly within limits
        if ip not in self.usage:
            return True

        # Get current counts from the lengths of the deques
        hourly_usage = len(self.usage[ip]['hourly'])
        daily_usage = len(self.usage[ip]['daily'])

        # Check against defined limits
        if hourly_usage > self.hourly_limit or daily_usage > self.daily_limit:
            return False  # Limit exceeded

        return True  # Within limits

    def get_usage(self, ip):
        """
        Gets the current hourly and daily usage counts for an IP.
        """
        # Return zero usage if the IP hasn't been tracked yet
        if ip not in self.usage:
            return {'hourly': 0, 'daily': 0}

        hourly_usage = len(self.usage[ip]['hourly'])
        daily_usage = len(self.usage[ip]['daily'])

        return {'hourly': hourly_usage, 'daily': daily_usage}
