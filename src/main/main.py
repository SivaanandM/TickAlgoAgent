import ast
import os
import traceback
import argparse
import sys
import pandas as pd
sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
from kafka import KafkaConsumer
from json import loads
import threading
from src.loghandler import log
from src.main.algo_agent_object import AlgoAgentObjects as agentObj
from src.commonlib.firebase_utils import FireBaseUtils
from src.pandaframe.prev_indicators import prevIndicators
from src.indicators.indicators import Indicators

logger = log.setup_custom_logger('AlgoAgent')



class ConsumerAgent(object):

    ohlc_consumer = None
    indicator_obj = None

    def __init__(self, args_topic, args_kafkadetails, args_symbol, args_marketdate, arg_prevdate):
        agentObj.topic = args_topic
        agentObj.kafka = args_kafkadetails
        agentObj.market_date = args_marketdate
        agentObj.symbol = args_symbol
        agentObj.prev_market_date = arg_prevdate
        self.ohlc_consumer = KafkaConsumer(str(agentObj.topic),
                      bootstrap_servers=[str(agentObj.kafka)],
                      auto_offset_reset='earliest',
                      enable_auto_commit=True,
                      group_id='agent',
                      value_deserializer=lambda x: loads(x.decode('utf-8')))

    def startlisten(self):
        indicator_obj = Indicators()
        logger.info("Algo Agent Strated Listening ticks for "+ agentObj.symbol +", Topic Id:"+agentObj.topic)
        try:
            for message in self.ohlc_consumer:
                message = message.value
                indicator_obj.algo(message)
        except Exception as ex:
            logger.error(traceback.format_exc())

    def loadDFs_with_prev_data(self, date, symbol, contract_type="STK"):
        try:
            logger.info("Trying to get previous day bar data from firebase")
            fbobj = FireBaseUtils()
            csv_path = fbobj.get_file_from_firebaseStorage(fbobj.get_blob_path(date,symbol,contract_type))
            logger.info("CSV downloaded from firebase and saved in "+csv_path)
            data = pd.read_csv(csv_path)
            data['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
            data = data.set_index('time')
            data = data.tz_convert(tz='Asia/Kolkata')
            ti = data.loc[:, ['price']]
            agentObj.fast_min_pd_DF = ti.price.resample(str(agentObj.fast_min) + 'min').ohlc()
            agentObj.slow_min_pd_DF = ti.price.resample(str(agentObj.slow_min) + 'min').ohlc()
            logger.info("Panda dataframe resampled for fast and slow prev day data")
            pindi = prevIndicators()
            logger.info("Generating indicators for data frames")
            pindi.generate_indicator_serious()
            logger.info("All indicators gensrated sucessfull for previous day data")
            logger.info("**Fast dataframe with indicators")
            logger.info(agentObj.fast_min_pd_DF)
            logger.info("**Fast dataframe with indicators")
            logger.info(agentObj.slow_min_pd_DF)

        except Exception as ex:
            logger.error(traceback.format_exc())


    def startAgentEngine(self):
        try:
            logger.info("Algo Agent Preparing to Start")
            self.loadDFs_with_prev_data(agentObj.prev_market_date, agentObj.symbol, "STK")
            self.startlisten()
        except Exception as ex:
            logger.error(traceback.format_exc())


def cmd_param_handlers():
    try:
        logger.info("Tick Algo Agent - command param handlers")
        cmdLineParser = argparse.ArgumentParser("Tick Algo Agent :")
        cmdLineParser.add_argument("-k", "--kafka", action="store", type=str, dest="kafka",
                                   default="127.0.0.1:9092", help="Kafka server IP eg: 127.0.0.1:9092")
        cmdLineParser.add_argument("-t", "--topic", action="store", type=str, dest="topic",
                                   default="ADANIPORT", help="Kafka Producer Topic Name eg: 0")
        cmdLineParser.add_argument("-md", "--marketdate", action="store", type=str, dest="marketdate",
                                   default="20191031", help="Market Date eg: 20191025")
        cmdLineParser.add_argument("-pd", "--prevdate", action="store", type=str, dest="prevdate",
                                   default="20191030", help="Previous Market date eg: 20191025")
        cmdLineParser.add_argument("-s", "--symbol", action="store", type=str, dest="symbol",
                                   default="ADANIPORT", help="IB Symbol eg: INFY")
        args = cmdLineParser.parse_args()

        consObj = ConsumerAgent(args_topic=str(args.topic),
                                args_kafkadetails=str(args.kafka),
                                args_symbol=str(args.symbol),
                                args_marketdate=str(args.marketdate),
                                arg_prevdate=str(args.prevdate))
        consObj.startAgentEngine()


    except Exception as ex:
        logger.error(traceback.format_exc())
        logger.error(ex)



if __name__ == '__main__':
    logger.info("** Algo Agent Initiated Succesfully")
    cmd_param_handlers()
    # consobj = ConsumerAgent(
    #     args_topic=str("HRHD"),
    #     args_kafkadetails=str("127.0.0.1:9092"),
    #     args_symbol=str("TCS"),
    #     args_marketdate=str("20191030"),
    #     arg_prevdate=str("20191029")
    # )
    # logger.info("Base parameters initialized")
    consobj.startAgentEngine()

