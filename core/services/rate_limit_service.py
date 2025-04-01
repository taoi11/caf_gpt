import time
from collections import deque
from ipaddress import ip_network, ip_address

class RateLimitService:
    def __init__(self):
        self.hourly_limit = 10
        self.daily_limit = 30
        self.hourly_window = 3600  # 1 hour in seconds
        self.daily_window = 86400  # 24 hours in seconds
        self.whitelist = [
            ip_network('205.193.0.0/16'),
            # ip_network('127.0.0.1/32') # Whitelist localhost for development (Temporarily commented out for testing)
        ]
        self.usage = {}

    def is_whitelisted(self, ip):
        ip_addr = ip_address(ip)
        return any(ip_addr in network for network in self.whitelist)

    def increment(self, ip):
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

        return self.check_limits(ip)

    def check_limits(self, ip):
        if self.is_whitelisted(ip):
            return True
            
        # If IP not tracked yet, usage is 0, so limits are not exceeded
        if ip not in self.usage:
            return True

        hourly_usage = len(self.usage[ip]['hourly'])
        daily_usage = len(self.usage[ip]['daily'])

        if hourly_usage > self.hourly_limit or daily_usage > self.daily_limit:
            return False

        return True

    def get_usage(self, ip):
        if ip not in self.usage:
            return {'hourly': 0, 'daily': 0}

        hourly_usage = len(self.usage[ip]['hourly'])
        daily_usage = len(self.usage[ip]['daily'])

        return {'hourly': hourly_usage, 'daily': daily_usage}
