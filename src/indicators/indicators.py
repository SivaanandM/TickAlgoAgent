import sys,os
sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
import traceback
from src.loghandler import log
from concurrent.futures import ThreadPoolExecutor
from src.pandaframe.slow_df import SlowDF as SLDF
from src.pandaframe.fast_df import FastDF as FADF
from src.algos.sapm import Sapm as Sapm

logger = log.setup_custom_logger('AlgoAgent')



class Indicators(object):
    sapm_obj_one = None

    def __init__(self):
        self.sapm_obj_one = Sapm()

    def data_frame(self, ticks):
        SLDF.generate_slow_min_df(ticks)
        FADF.generate_fast_min_df(ticks)

    def exe_sapm(self, ticks):
        self.sapm_obj_one.do_samp(ticks)

    def algo(self, ticks):
        try:
            executors_list = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                if ticks.get('Price') is not None:
                    executors_list.append(executor.submit(self.data_frame(ticks)))
                    executors_list.append(executor.submit(self.exe_sapm(ticks)))

        except:
            # print(traceback.format_exc())
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    a = Indicators()
    a.algo("[[2123123, 12]]")

