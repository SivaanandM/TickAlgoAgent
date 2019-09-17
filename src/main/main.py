import ast
import os
import traceback
import sys
sys.path.append(os.getenv('TICKALGOAGENT'))
from kafka import KafkaConsumer
from json import loads
import threading
from src.loghandler import log
from src.main.algo_agent_object import AlgoAgentObjects as AB_Obj
from src.indicators.indicators import Indicators

logger = log.setup_custom_logger('AlgoAgent')
ohlc_consumer = KafkaConsumer("HRHD",
                         bootstrap_servers=['127.0.0.1:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='ohlc',
                         value_deserializer=lambda x: loads(x.decode('utf-8')))

class IndicatorConsumer(object):
    indicator_obj = Indicators()

    def start(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()
        return thread

    def run(self):
        for message in ohlc_consumer:
            message = message.value
            self.indicator_obj.algo(message)

def main():
    try:

        indi_consumer_obj = IndicatorConsumer()
        indicator_thread = indi_consumer_obj.start()

    except Exception as ex:
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    logger.info("** AlgoBot Initiated")
    main()
