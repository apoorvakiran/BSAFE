import logging
import os
from periodiq import PeriodiqMiddleware, cron
from ErgoAnalytics import ErgoMetrics
from ErgoAnalytics import StructuredDataStreaming
from ErgoAnalytics import ErgoReport

from .extensions import dramatiq

logger = logging.getLogger()

@dramatiq.actor(periodic=cron('* * * * *'))
def heartbeat():
    logger.info("Pulse")

@dramatiq.actor
def safety_score_analysis(mac_address, from_date, till_date):
    logger.info(f"Getting safety score for {mac_address}")
    index = os.getenv('ELASTIC_SEARCH_INDEX', 'iterate-labs-local-poc')
    host = os.getenv('ELASTIC_SEARCH_HOST')
    es_data = StructuredDataStreaming(streaming_source='elastic_search',
                                           streaming_settings=
                                           {"mac_address": mac_address,
                                            "from_date": from_date,
                                            "till_date": till_date,
                                            "host": host, "index": index,
                                            "data_format_code": "2"})
    logger.info(f"Retrieved all data for {mac_address}")
    if es_data.time is not None:
        logger.info(f"Has data to run analysis on for {mac_address}")
        metrics = ErgoMetrics(es_data)
        logger.info(f"Metrics generated for {mac_address}")
        report = ErgoReport(
            'http',
            metrics,
            f"Bearer {os.getenv('INFINITY_GAUNTLET_AUTH')}",
            f"{os.getenv('INFINITY_GAUNTLET_URL')}/api/v1/safety_scores",
            mac_address
        )
        logger.info(f"{report._sent.status_code} {report._sent.json()}")
        logger.info(f"Created safety_score for {mac_address}")
    else:
        logger.info(f"No values to analyze for {mac_address}")
