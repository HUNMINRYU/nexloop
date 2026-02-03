"""
IP-based rate limiting utility for non-authenticated requests.
Uses in-memory cache with time-based expiration.
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple


class RateLimiter:
    """Simple in-memory rate limiter based on IP address."""

    def __init__(self):
        # Store: {ip_address: (request_count, reset_time)}
        self._cache: Dict[str, Tuple[int, datetime]] = {}

    def check_limit(self, ip_address: str, max_requests: int = 3, window_hours: int = 24) -> bool:
        """
        Check if the IP address has exceeded the rate limit.

        Args:
            ip_address: The IP address to check
            max_requests: Maximum number of requests allowed
            window_hours: Time window in hours

        Returns:
            True if request is allowed, False if limit exceeded
        """
        now = datetime.now()

        # Clean up expired entries
        self._cleanup()

        if ip_address not in self._cache:
            # First request from this IP
            reset_time = now + timedelta(hours=window_hours)
            self._cache[ip_address] = (1, reset_time)
            return True

        count, reset_time = self._cache[ip_address]

        # Check if the time window has expired
        if now >= reset_time:
            # Reset the counter
            new_reset_time = now + timedelta(hours=window_hours)
            self._cache[ip_address] = (1, new_reset_time)
            return True

        # Check if limit is exceeded
        if count >= max_requests:
            return False

        # Increment counter
        self._cache[ip_address] = (count + 1, reset_time)
        return True

    def get_remaining(self, ip_address: str, max_requests: int = 3) -> int:
        """
        Get remaining requests for an IP address.

        Args:
            ip_address: The IP address to check
            max_requests: Maximum number of requests allowed

        Returns:
            Number of remaining requests
        """
        now = datetime.now()

        if ip_address not in self._cache:
            return max_requests

        count, reset_time = self._cache[ip_address]

        if now >= reset_time:
            return max_requests

        return max(0, max_requests - count)

    def _cleanup(self):
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_ips = [ip for ip, (_, reset_time) in self._cache.items() if now >= reset_time]
        for ip in expired_ips:
            del self._cache[ip]


# Global rate limiter instance
_rate_limiter = RateLimiter()


def check_rate_limit(ip_address: str, max_requests: int = 3) -> bool:
    """
    Check if the IP address has exceeded the rate limit.

    Args:
        ip_address: The IP address to check
        max_requests: Maximum number of requests allowed (default: 3)

    Returns:
        True if request is allowed, False if limit exceeded
    """
    return _rate_limiter.check_limit(ip_address, max_requests)


def get_remaining_requests(ip_address: str, max_requests: int = 3) -> int:
    """
    Get remaining requests for an IP address.

    Args:
        ip_address: The IP address to check
        max_requests: Maximum number of requests allowed (default: 3)

    Returns:
        Number of remaining requests
    """
    return _rate_limiter.get_remaining(ip_address, max_requests)
