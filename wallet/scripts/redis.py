import redis, os

# Set up a connection pool. Adjust the host, port, and db as per your configuration
pool = redis.ConnectionPool(host=os.getenv('REDIS_URL'), port=os.getenv('REDIS_PORT'), db='0')

# This won't create a connection immediately but will use the pool to manage connections.
redis_conn = redis.Redis(connection_pool=pool)