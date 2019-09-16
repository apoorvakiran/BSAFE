import logging
import os
from periodiq import PeriodiqMiddleware, cron
from ErgoAnalytics import ErgoMetrics
from ErgoAnalytics import StructuredDataStreaming

from .extensions import dramatiq

logger = logging.getLogger()

@dramatiq.actor
def process_job(job_id):
    logger.info("Done job #%s.", job_id)


@dramatiq.actor(periodic=cron('* * * * *'))
def heartbeat():
    logger.info("Pulse.")

@dramatiq.actor
def safety_score_analysis(mac_address, from_date, till_date):
    logger.info("Getting safety score for #%s.", mac_address)
    index = os.getenv('ELASTIC_SEARCH_INDEX', 'iterate-labs-local-poc')
    es_safe_data = StructuredDataStreaming(streaming_source='elastic_search',
                                           streaming_settings=
                                           {"mac_address": mac_address,
                                            "from_date": from_date,
                                            "till_date": till_date,
                                            "hosts": None, "index": index,
                                            "data_format_code": "2"})
    mets = ErgoMetrics(es_safe_data)
    logger.info("Created safety_score for #%s.", mac_address)

