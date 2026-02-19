"""
Custom cache key function for use with Django's KEY_FUNCTION cache setting.

This replicates the key construction logic previously found in
esp.utils.memcached_multikey.CacheClass.make_key, so that we can use
Django's built-in PyLibMCCache backend directly while preserving the same
key format (including truncation/hashing for oversized keys).
"""
import hashlib
import logging

from esp.utils import ascii

logger = logging.getLogger(__name__)

MAX_KEY_LENGTH = 250
NO_HASH_PREFIX = "NH_"
HASH_PREFIX = "H_"


def make_cache_key(key, key_prefix, version):
    """
    Django KEY_FUNCTION compatible cache key constructor.

    Produces keys of the form:
        NH_<key_prefix><key>              (when short enough)
        H_<md5hex>_<truncated_rawkey>     (when the key would be too long)

    The key_prefix comes from the CACHES KEY_PREFIX setting, which replaces
    the old settings.CACHE_PREFIX mechanism.
    """
    # Build the versioned Django prefix (e.g. ":1:") to account for its length
    django_prefix = "%s:%s:" % (key_prefix, version)
    raw_key = ascii(NO_HASH_PREFIX + key_prefix + key)
    real_max_length = MAX_KEY_LENGTH - len(django_prefix)

    if len(raw_key) <= real_max_length:
        return raw_key
    else:
        hash_key = HASH_PREFIX + hashlib.md5(key.encode("UTF-8")).hexdigest()
        return hash_key + '_' + raw_key[:real_max_length - len(hash_key) - 1]
