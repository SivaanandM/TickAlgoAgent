import os
import sys

sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
from src.main.algo_agent_object import AlgoAgentObjects as abObj
from src.pandaframe import slow_indicators as indi_obj
# from src.loghandler import log
import traceback
import time
# os.environ['TZ'] = 'Asia/Kolkata'
# time.tzset()
import pandas as pd

# logger = abObj.log


class SlowDF(object):
    def __init__(self):
        pass

    @staticmethod
    def generate_slow_min_df(ticks):

        def get_ohlc():
            try:
                data = pd.DataFrame(abObj.slow_min_ticks, columns=['time', 'price'])
                data['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
                data = data.set_index('time')
                data = data.tz_convert(tz='Asia/Kolkata')
                ti = data.loc[:, ['price']]
                slow_min_bars = ti.price.resample(str(abObj.slow_min)+'min').ohlc()
                for index, row in slow_min_bars.iterrows():
                    # print('*', row)
                    abObj.slow_min_pd_DF = abObj.slow_min_pd_DF.append(row, sort=False)
                    break
                indi_obj.load_indicators()
            except:
                # print(traceback.format_exc())
                abObj.log.error(traceback.format_exc())
        tick_time = ticks.get('Timestamp')
        tick_price = ticks.get('Price')
        try:
            if len(abObj.slow_min_ticks) > 0:

                if (int(str(time.strftime("%M", time.localtime(int(tick_time)))))) > abObj.cur_slow_min-1:
                    # print('@', abObj.cur_slow_min)
                    # print(abObj.slow_min_ticks[0][0], ' - ', abObj.slow_min_ticks[len(abObj.slow_min_ticks)-1][0])
                    get_ohlc()
                    abObj.slow_min_ticks.clear()
                    abObj.slow_min_ticks.append([tick_time, tick_price])
                    abObj.cur_slow_min = (int(str(time.strftime("%M", time.localtime(int(tick_time)))))) + abObj.slow_min
                else:
                    abObj.slow_min_ticks.append([tick_time, tick_price])

                if (int(str(time.strftime("%M", time.localtime(int(tick_time))))) == 0) and abObj.cur_slow_min >= 59:
                    abObj.cur_slow_min = abObj.cur_slow_min - 60
            else:
                abObj.cur_slow_min = int(str(time.strftime("%M", time.localtime(int(tick_time))))) + abObj.slow_min
                abObj.slow_min_ticks.append([tick_time, tick_price])

        except:
            # print(traceback.format_exc())
            abObj.log.error(traceback.format_exc())



