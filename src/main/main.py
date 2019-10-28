import ast
import os
import traceback
import sys
sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
from kafka import KafkaConsumer
from json import loads
import threading
from src.loghandler import log
from src.main.algo_agent_object import AlgoAgentObjects as AB_Obj
from src.indicators.indicators import Indicators

logger = log.setup_custom_logger('AlgoAgent')



class IndicatorConsumer(object):

    TOPIC = "0"
    ohlc_consumer = None
    indicator_obj = Indicators()

    def __init__(self, topic):
        self.TOPIC = topic
        self.ohlc_consumer = KafkaConsumer("HRHD",
                      bootstrap_servers=['127.0.0.1:9092'],
                      auto_offset_reset='earliest',
                      enable_auto_commit=True,
                      group_id='ohlc',
                      value_deserializer=lambda x: loads(x.decode('utf-8')))

    def run(self):
        for message in ohlc_consumer:
            message = message.value
            self.indicator_obj.algo(message)

def main(topic_to_listen):
    try:
        indi_consumer_obj = IndicatorConsumer(topic_to_listen)
        indicator_thread = indi_consumer_obj.run()
    except Exception as ex:
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    logger.info("** AlgoBot Initiated")
    main("HRHD")
