import logging
from periodiq import PeriodiqMiddleware, cron

from .extensions import dramatiq

logger = logging.getLogger(__name__ + '.tasks')

@dramatiq.actor
def process_job(job_id):
    logger.info("Done job #%s.", job_id)


@dramatiq.actor(periodic=cron('* * * * *'))
def heartbeat():
    logger.info("Pulse.")
