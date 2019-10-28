from configparser import ConfigParser
import os
import sys
sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
import pandas as pd


class AlgoAgentObjects:
    # General config to set config file
    parser = ConfigParser()
    os.environ['TICKALGOAGENT_CONFIG'] = os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")]+'/config/config.ini'
    parser.read(os.getenv("TICKALGOAGENT_CONFIG"))
    indicator_thread = None
    hrhd_thread = None
    sapm_thread = None
    start_sapm = True

    market_date = "20191023"
    prev_market_date = "20191022"
    # all below used in fast min data frame
    fast_min_ticks = []
    fast_min = int(parser.get('dataframes', 'fast_df'))
    cur_fast_min = 0
    fast_min_pd_DF = pd.DataFrame([])

    # all below used in slow min data frame
    slow_min_ticks = []
    slow_min = int(parser.get('dataframes', 'slow_df'))
    cur_slow_min = 0
    slow_min_pd_DF = pd.DataFrame([])
    # end

    # General flags
    long_flags = {'FA_SAPM': 0, 'FA_MAEMA': 0, 'FA_ADX': 0, 'FA_MACD': 0, 'FA_RSI': 0,
                  'SL_SAPM': 0, 'SL_MAEMA': 0, 'SL_ADX': 0, 'SL_MACD': 0, 'SL_RSI': 0}

    short_flags = {'FA_SAPM': 0, 'FA_MAEMA': 0, 'FA_ADX': 0, 'FA_MACD': 0, 'FA_RSI': 0,
                   'SL_SAPM': 0, 'SL_MAEMA': 0, 'SL_ADX': 0, 'SL_MACD': 0, 'SL_RSI': 0}


    @staticmethod
    def get_with_base_path(head, key):
        return os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent/")] + AlgoAgentObjects.parser.get(head, key)

    @staticmethod
    def get_value(head, key):
        return AlgoAgentObjects.parser.get(head, key)

    @staticmethod
    def update_config_values(section, key, value):
        AlgoAgentObjects.parser.set(section, key, value)