from slowapi import Limiter
from slowapi.util import get_remote_address

# We use an in-memory limiter using the client's IP address.
limiter = Limiter(key_func=get_remote_address)
