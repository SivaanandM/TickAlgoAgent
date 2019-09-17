import sys,os
sys.path.append(os.getenv('TICKALGOAGENT'))
from src.main.algo_agent_object import AlgoAgentObjects as abObj
from src.pandaframe import fast_indicators as indi_obj
import traceback
from src.loghandler import log
import time
import pandas as pd

logger = log.setup_custom_logger('root')


class FastDF(object):
    def __init__(self):
        pass

    @staticmethod
    def generate_fast_min_df(ticks):

        def get_ohlc():
            try:
                data = pd.DataFrame(abObj.fast_min_ticks, columns=['time', 'price'])
                data['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
                data = data.set_index('time')
                data = data.tz_convert(tz='Asia/Kolkata')
                ti = data.loc[:, ['price']]
                fast_min_bars = ti.price.resample(str(abObj.fast_min)+'min').ohlc()
                for index, row in fast_min_bars.iterrows():
                    abObj.fast_min_pd_DF = abObj.fast_min_pd_DF.append(row, sort=False)
                    break
                indi_obj.load_indicators()
            except:
                print(traceback.format_exc())
                logger.error(traceback.format_exc())

        tick_time = ticks.get('Timestamp')
        tick_price = ticks.get('Price')
        try:
            if len(abObj.fast_min_ticks) > 0:
                if int(str(time.strftime("%M", time.localtime(int(tick_time))))) > abObj.cur_fast_min - 1:
                    get_ohlc()
                    abObj.fast_min_ticks.clear()
                    abObj.fast_min_ticks.append([tick_time, tick_price])
                    abObj.cur_fast_min = int(str(time.strftime("%M", time.localtime(int(tick_time))))) + abObj.fast_min
                else:
                    abObj.fast_min_ticks.append([tick_time, tick_price])
                if (int(str(time.strftime("%M", time.localtime(int(tick_time))))) == 0) and abObj.cur_fast_min >= 59:
                    abObj.cur_fast_min = abObj.cur_fast_min - 60
            else:
                abObj.cur_fast_min = int(str(time.strftime("%M", time.localtime(int(tick_time))))) + abObj.fast_min
                abObj.fast_min_ticks.append([tick_time, tick_price])
        except:
            print(traceback.format_exc())
            logger.error(traceback.format_exc())

