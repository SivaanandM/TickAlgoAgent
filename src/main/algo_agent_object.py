from configparser import ConfigParser
import os
import sys
sys.path.append(os.getenv('TICKALGOAGENT'))
import pandas as pd


class AlgoAgentObjects:
    # General config to set config file
    parser = ConfigParser()
    os.environ['TICKALGOAGENT_CONFIG'] = os.path.join(os.getenv('TICKALGOAGENT'),'config/config.ini')
    parser.read(os.getenv("TICKALGOAGENT_CONFIG"))
    indicator_thread = None
    hrhd_thread = None
    sapm_thread = None
    start_sapm = False

    # all below used in fast min data frame
    fast_min_ticks = []
    fast_min = int(parser.get('common', 'fast_df'))
    cur_fast_min = 0
    fast_min_pd_DF = pd.DataFrame([])

    # all below used in slow min data frame
    slow_min_ticks = []
    slow_min = int(parser.get('common', 'slow_df'))
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
        return os.getenv('TICKSTREAM') + AlgoAgentObjects.parser.get(head, key)

    @staticmethod
    def get_value(head, key):
        return AlgoAgentObjects.parser.get(head, key)

    @staticmethod
    def update_config_values(section, key, value):
        AlgoAgentObjects.parser.set(section, key, value)