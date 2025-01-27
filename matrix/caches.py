import logging
from django.core.cache.backends.memcached import PyMemcacheCache

# Use Django's logging system (Sentry will automatically capture these)
logger = logging.getLogger(__name__)


class GracefulMemcachedBackend(PyMemcacheCache):
    def __init__(self, server, params):
        super().__init__(server, params)

    def get(self, key, default=None, version=None):
        try:
            return super().get(key, default, version)
        except (ConnectionRefusedError, OSError) as e:
            logger.error(f"Memcached GET failed for key: {key}. Error: {e}")
            return default  # Return default value if Memcached is down

    def set(self, key, value, timeout=None, version=None):
        try:
            super().set(key, value, timeout, version)
        except (ConnectionRefusedError, OSError) as e:
            logger.error(f"Memcached SET failed for key: {key}. Error: {e}")
            pass

    def delete(self, key, version=None):
        try:
            super().delete(key, version)
        except (ConnectionRefusedError, OSError) as e:
            logger.error(f"Memcached DELETE failed for key: {key}. Error: {e}")
            pass
