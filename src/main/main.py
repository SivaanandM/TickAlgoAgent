import datetime
import os
from datetime import timezone
import time
import pytz

# time.tzset()
# tz = pytz.timezone('Asia/Kolkata')

import os
import traceback
import argparse
import sys
sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
from kafka import KafkaConsumer
import pandas as pd
from src.loghandler import log
from src.main.algo_agent_object import AlgoAgentObjects as agentObj
from src.commonlib.firebase_utils import FireBaseUtils
from src.pandaframe.prev_indicators import prevIndicators
from src.indicators.indicators import Indicators
from json import loads
logger=None
class ConsumerAgent(object):

    ohlc_consumer = None
    indicator_obj = None
    exit_algo = None
    exit_algo_315pm = None
    tick_df = None

    def __init__(self, args_topic, args_kafkadetails, args_symbol, args_marketdate, arg_prevdate):
        agentObj.log = log.setup_custom_logger(args_topic)
        agentObj.topic = args_topic
        agentObj.kafka = args_kafkadetails
        agentObj.market_date = args_marketdate
        agentObj.symbol = args_symbol
        agentObj.prev_market_date = arg_prevdate
        if agentObj.backtest is False:
            self.exit_algo = datetime.datetime.strptime(agentObj.market_date + ' 09:45:00', '%Y%m%d %H:%M:%S')
            self.exit_algo_315pm = self.exit_algo.timestamp()
        else:
            self.exit_algo = datetime.datetime.strptime(agentObj.market_date + ' 15:15:00', '%Y%m%d %H:%M:%S')
            self.exit_algo_315pm = self.exit_algo.timestamp()
        self.tick_df = pd.DataFrame(None, columns=['Timestamp', 'Price'])
        self.ohlc_consumer = KafkaConsumer(bootstrap_servers=['localhost:9092'],
                      auto_offset_reset='earliest',
                      enable_auto_commit=True,
                      value_deserializer=lambda x: loads(x.decode('utf-8')))

    def export_dataframe(self, message):
        try:
            if not os.path.exists(os.path.join("/tmp", agentObj.market_date)):
                os.makedirs(os.path.join("/tmp", agentObj.market_date))
            dfs_path = os.path.join("/tmp", agentObj.market_date)
            agentObj.fast_min_pd_DF.to_csv(os.path.join(dfs_path, agentObj.symbol+"_fast_data_frames.csv"), header=True)
            agentObj.slow_min_pd_DF.to_csv(os.path.join(dfs_path, agentObj.symbol+"_slow_data_frames.csv"), header=True)
            self.tick_df.to_csv(os.path.join(dfs_path, agentObj.symbol + "_ticks.csv"), header=True)
            sys.exit()
        except Exception as ex:
            agentObj.log.error(traceback.format_exc())
            sys.exit()

    def startlisten(self):
        indicator_obj = Indicators()
        agentObj.log.info("Algo Agent Started Listening ticks for " + agentObj.symbol + ", Topic Id:"+agentObj.topic)
        print("In Liostening")
        self.ohlc_consumer.subscribe([str(agentObj.topic)])
        try:
            for message in self.ohlc_consumer:
                # print(message.value)
                message = message.value
                if (message.get('Timestamp') is not None) and (message.get('Price') is not None):
                    self.tick_df.loc[len(self.tick_df)] = [message.get('Timestamp'), message.get('Price')]
                    if float(message.get('Timestamp')) < self.exit_algo_315pm:
                        indicator_obj.algo(message)
                    else:
                        self.export_dataframe(message)
        except Exception as ex:
            agentObj.log.error(traceback.format_exc())

    def loadDFs_with_prev_data(self, date, symbol, contract_type="STK"):
        try:
            agentObj.log.info("Trying to get previous day bar data from firebase")
            fbobj = FireBaseUtils()
            csv_path = fbobj.get_file_from_firebaseStorage(fbobj.get_blob_path(date,symbol,contract_type))
            agentObj.log.info("CSV downloaded from firebase and saved in "+csv_path)
            data = pd.read_csv(csv_path)
            data['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
            data = data.set_index('time')
            data = data.tz_convert(tz='Asia/Kolkata')
            ti = data.loc[:, ['price']]
            agentObj.fast_min_pd_DF = ti.price.resample(str(agentObj.fast_min) + 'min').ohlc()
            agentObj.slow_min_pd_DF = ti.price.resample(str(agentObj.slow_min) + 'min').ohlc()
            agentObj.log.info("Panda dataframe resampled for fast and slow prev day data")
            pindi = prevIndicators()
            agentObj.log.info("Generating indicators for data frames")
            pindi.generate_indicator_serious()
            agentObj.log.info("All indicators gensrated sucessfull for previous day data")
            agentObj.log.info("**Fast dataframe with indicators")
            agentObj.fast_min_pd_DF = agentObj.fast_min_pd_DF[:-1]
            agentObj.log.info(agentObj.fast_min_pd_DF)
            agentObj.log.info("**Fast dataframe with indicators")
            agentObj.slow_min_pd_DF = agentObj.slow_min_pd_DF[:-1]
            agentObj.log.info(agentObj.slow_min_pd_DF)

        except Exception as ex:
            agentObj.log.error(traceback.format_exc())


    def startAgentEngine(self):
        try:
            agentObj.log.info("Algo Agent Preparing to Start")
            self.loadDFs_with_prev_data(agentObj.prev_market_date, agentObj.symbol, "STK")
            self.startlisten()
        except Exception as ex:
            agentObj.log.error(traceback.format_exc())


def cmd_param_handlers():
    try:
        # agentObj.log.info("Tick Algo Agent - command param handlers")
        cmdLineParser = argparse.ArgumentParser("Tick Algo Agent :")
        cmdLineParser.add_argument("-k", "--kafka", action="store", type=str, dest="kafka",
                                   default="127.0.0.1:9092", help="Kafka server IP eg: 127.0.0.1:9092")
        cmdLineParser.add_argument("-t", "--topic", action="store", type=str, dest="topic",
                                   default="CIPLA", help="Kafka Producer Topic Name eg: 0")
        cmdLineParser.add_argument("-md", "--marketdate", action="store", type=str, dest="marketdate",
                                   default="20200424", help="Market Date eg: 20191025")
        cmdLineParser.add_argument("-pd", "--prevdate", action="store", type=str, dest="prevdate",
                                   default="20200423", help="Previous Market date eg: 20191025")
        cmdLineParser.add_argument("-s", "--symbol", action="store", type=str, dest="symbol",
                                   default="CIPLA", help="IB Symbol eg: INFY")
        cmdLineParser.add_argument("-bt", "--backtest", action="store", type=bool, dest="backtest",
                                   default=True, help="Back Test eg : True or False")

        args = cmdLineParser.parse_args()
        agentObj.backtest = bool(args.backtest)
        consObj = ConsumerAgent(args_topic=str(args.topic),
                                args_kafkadetails=str(args.kafka),
                                args_symbol=str(args.symbol),
                                args_marketdate=str(args.marketdate),
                                arg_prevdate=str(args.prevdate))
        consObj.startAgentEngine()


    except Exception as ex:
        agentObj.log.error(traceback.format_exc())
        agentObj.log.error(ex)



if __name__ == '__main__':
    # agentObj.log.info("** Algo Agent Initiated Succesfully")
    cmd_param_handlers()

    # # Below commands to execute individually
    # consobj = ConsumerAgent(
    #     args_topic=str("ADANIPORT"),
    #     args_kafkadetails=str("localhost:9092"),
    #     args_symbol=str("ADANIPORT"),
    #     args_marketdate=str("20200417"),
    #     arg_prevdate=str("20200416")
    # )
    # consobj.startAgentEngine()
