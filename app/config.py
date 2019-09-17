import os
from dramatiq.brokers.redis import RedisBroker

def make_dir(dir_path):
  try:
    if not os.path.exists(dir_path):
      os.makedirs(dir_path, exist_ok=True)
  except Exception as e:
    raise e

DRAMATIQ_BROKER = RedisBroker
DRAMATIQ_BROKER_URL = "redis://" + os.getenv('BROKER_URL', 'localhost:6379/0')
INSTANCE_FOLDER_PATH = os.path.join('/var/tmp', 'instance')
make_dir(INSTANCE_FOLDER_PATH)
LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')
make_dir(LOG_FOLDER)
