import os
from dramatiq.brokers.redis import RedisBroker

DRAMATIQ_BROKER = RedisBroker
DRAMATIQ_BROKER_URL = "redis://" + os.environ.get('BROKER_URL', 'localhost:6379/0')
