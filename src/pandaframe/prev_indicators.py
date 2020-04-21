import sys,os
import sys

sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
from src.main.algo_agent_object import AlgoAgentObjects as agentObj
# from src.loghandler import log
import pandas as pd
import traceback

# logger = agentObj.log

class prevIndicators(object):

    def moving_average(self):
        try:
            n = int(agentObj.get_value("ma", "interval"))
            FMA = pd.Series(agentObj.fast_min_pd_DF['close'].rolling(n, min_periods=n).mean(), name='MA')
            agentObj.fast_min_pd_DF = agentObj.fast_min_pd_DF.join(FMA)
            SMA = pd.Series(agentObj.slow_min_pd_DF['close'].rolling(n, min_periods=n).mean(), name='MA')
            agentObj.slow_min_pd_DF = agentObj.slow_min_pd_DF.join(SMA)

        except Exception as ex:
            logger.error(traceback.format_exc())

    def exponential_moving_average(dself):
        try:
            n = int(agentObj.get_value("ema", "interval"))
            FEMA = pd.Series(agentObj.fast_min_pd_DF['close'].ewm(span=n, min_periods=n).mean(), name='EMA')
            agentObj.fast_min_pd_DF = agentObj.fast_min_pd_DF.join(FEMA)
            SEMA = pd.Series(agentObj.slow_min_pd_DF['close'].ewm(span=n, min_periods=n).mean(), name='EMA')
            agentObj.slow_min_pd_DF = agentObj.slow_min_pd_DF.join(SEMA)

        except Exception as ex:
            agentObj.log.error(traceback.format_exc())

    def macd(self):
        try:
            n_fast = int(agentObj.get_value("macd", "fast_interval"))
            n_slow = int(agentObj.get_value("macd", "slow_interval"))
            macdsign_n = int(agentObj.get_value("macd", "MACDsign_n"))

            FEMAfast = pd.Series(agentObj.fast_min_pd_DF['close'].ewm(span=n_fast, min_periods=n_slow).mean())
            FEMAslow = pd.Series(agentObj.fast_min_pd_DF['close'].ewm(span=n_slow, min_periods=n_slow).mean())
            FMACD = pd.Series(FEMAfast - FEMAslow, name='MACD')
            FMACDsign = pd.Series(FMACD.ewm(span=macdsign_n, min_periods=macdsign_n).mean(), name='MACDsign')
            FMACDdiff = pd.Series(FMACD - FMACDsign, name='MACDdiff')
            agentObj.fast_min_pd_DF = agentObj.fast_min_pd_DF.join(FMACD)
            agentObj.fast_min_pd_DF = agentObj.fast_min_pd_DF.join(FMACDsign)
            agentObj.fast_min_pd_DF = agentObj.fast_min_pd_DF.join(FMACDdiff)

            SEMAfast = pd.Series(agentObj.slow_min_pd_DF['close'].ewm(span=n_fast, min_periods=n_slow).mean())
            SEMAslow = pd.Series(agentObj.slow_min_pd_DF['close'].ewm(span=n_slow, min_periods=n_slow).mean())
            SMACD = pd.Series(SEMAfast - SEMAslow, name='MACD')
            SMACDsign = pd.Series(SMACD.ewm(span=macdsign_n, min_periods=macdsign_n).mean(), name='MACDsign')
            SMACDdiff = pd.Series(SMACD - SMACDsign, name='MACDdiff')
            agentObj.slow_min_pd_DF = agentObj.slow_min_pd_DF.join(SMACD)
            agentObj.slow_min_pd_DF = agentObj.slow_min_pd_DF.join(SMACDsign)
            agentObj.slow_min_pd_DF = agentObj.slow_min_pd_DF.join(SMACDdiff)

        except Exception as ex:
            agentObj.log.error(traceback.format_exc())

    def average_directional_movement_index_fastDF(self):
        try:
            n = int(agentObj.get_value("adx", "interval"))
            n_ADX = int(agentObj.get_value("adx", "interval_ADX"))
            i = 0
            UpI = []
            DoI = []
            for row in agentObj.fast_min_pd_DF.iterrows():
                if i != 0:
                    UpMove = agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i]]['high'] - agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i - 1]]['high']
                    DoMove = agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i - 1]]['low'] - agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i]]['low']
                    if UpMove > DoMove and UpMove > 0:
                        UpD = UpMove
                    else:
                        UpD = 0
                    UpI.append(UpD)
                    if DoMove > UpMove and DoMove > 0:
                        DoD = DoMove
                    else:
                        DoD = 0
                    DoI.append(DoD)
                i = i + 1
            i = 0
            TR_l = [0]
            for row in agentObj.fast_min_pd_DF.iterrows():
                if i != 0:
                    TR = max(agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i]]['high'], agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i - 1]]['close']) - min(
                        agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i]]['low'], agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i - 1]]['close'])
                    TR_l.append(TR)
                i = i + 1
            TR_s = pd.Series(TR_l)
            ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean())
            UpI = pd.Series(UpI)
            DoI = pd.Series(DoI)
            PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean() / ATR, name='PosDI')
            NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean() / ATR, name='NegDI')
            ADX = pd.Series((abs(PosDI - NegDI) / (PosDI + NegDI)).ewm(span=n_ADX, min_periods=n_ADX).mean(),
                            name='ADX')
            agentObj.fast_min_pd_DF['ADX'] = ADX.tolist()
            agentObj.fast_min_pd_DF['PosDI'] = PosDI.tolist()
            agentObj.fast_min_pd_DF['NegDI'] = NegDI.tolist()

        except Exception as ex:
            agentObj.log.error(traceback.format_exc())

    def average_directional_movement_index_slowDF(self):
        try:
            n = int(agentObj.get_value("adx", "interval"))
            n_ADX = int(agentObj.get_value("adx", "interval_ADX"))
            i = 0
            UpI = []
            DoI = []
            for row in agentObj.slow_min_pd_DF.iterrows():
                if i != 0:
                    UpMove = agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i]]['high'] - agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i - 1]]['high']
                    DoMove = agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i - 1]]['low'] - agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i]]['low']
                    if UpMove > DoMove and UpMove > 0:
                        UpD = UpMove
                    else:
                        UpD = 0
                    UpI.append(UpD)
                    if DoMove > UpMove and DoMove > 0:
                        DoD = DoMove
                    else:
                        DoD = 0
                    DoI.append(DoD)
                i = i + 1
            i = 0
            TR_l = [0]
            for row in agentObj.slow_min_pd_DF.iterrows():
                if i != 0:
                    TR = max(agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i]]['high'], agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i - 1]]['close']) - min(
                        agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i]]['low'], agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i - 1]]['close'])
                    TR_l.append(TR)
                i = i + 1
            TR_s = pd.Series(TR_l)
            ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean())
            UpI = pd.Series(UpI)
            DoI = pd.Series(DoI)
            PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean() / ATR, name='PosDI')
            NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean() / ATR, name='NegDI')
            ADX = pd.Series((abs(PosDI - NegDI) / (PosDI + NegDI)).ewm(span=n_ADX, min_periods=n_ADX).mean(),
                            name='ADX')
            agentObj.slow_min_pd_DF['ADX'] = ADX.tolist()
            agentObj.slow_min_pd_DF['PosDI'] = PosDI.tolist()
            agentObj.slow_min_pd_DF['NegDI'] = NegDI.tolist()
        except Exception as ex:
            agentObj.log.error(traceback.format_exc())

    def relative_strength_index_fastDF(self):
        try:
            n = int(agentObj.get_value("rsi", "interval"))
            i = 0
            UpI = [0]
            DoI = [0]
            for row in agentObj.fast_min_pd_DF.iterrows():
                if (i != 0):
                    UpMove = agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i]]['high'] - agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i - 1]]['high']
                    DoMove = agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i - 1]]['low'] - agentObj.fast_min_pd_DF.loc[agentObj.fast_min_pd_DF.index[i]]['low']
                    if UpMove > DoMove and UpMove > 0:
                        UpD = UpMove
                    else:
                        UpD = 0
                    UpI.append(UpD)
                    if DoMove > UpMove and DoMove > 0:
                        DoD = DoMove
                    else:
                        DoD = 0
                    DoI.append(DoD)
                i = i + 1
            UpI = pd.Series(UpI)
            DoI = pd.Series(DoI)
            PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean())
            NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean())
            RSI = pd.Series(PosDI / (PosDI + NegDI), name='RSI')
            agentObj.fast_min_pd_DF['RSI'] = RSI.tolist()
        except Exception as ex:
            agentObj.log.error(traceback.format_exc())

    def relative_strength_index_slowDF(self):
        try:
            n = int(agentObj.get_value("rsi", "interval"))
            i = 0
            UpI = [0]
            DoI = [0]
            for row in agentObj.slow_min_pd_DF.iterrows():
                if (i != 0):
                    UpMove = agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i]]['high'] - \
                             agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i - 1]]['high']
                    DoMove = agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i - 1]]['low'] - \
                             agentObj.slow_min_pd_DF.loc[agentObj.slow_min_pd_DF.index[i]]['low']
                    if UpMove > DoMove and UpMove > 0:
                        UpD = UpMove
                    else:
                        UpD = 0
                    UpI.append(UpD)
                    if DoMove > UpMove and DoMove > 0:
                        DoD = DoMove
                    else:
                        DoD = 0
                    DoI.append(DoD)
                i = i + 1
            UpI = pd.Series(UpI)
            DoI = pd.Series(DoI)
            PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean())
            NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean())
            RSI = pd.Series(PosDI / (PosDI + NegDI), name='RSI')
            agentObj.slow_min_pd_DF['RSI'] = RSI.tolist()
        except Exception as ex:
            agentObj.log.error(traceback.format_exc())


    def generate_indicator_serious(self):
        try:
            self.moving_average()
            self.exponential_moving_average()
            self.macd()
            self.average_directional_movement_index_fastDF()
            self.average_directional_movement_index_slowDF()
            self.relative_strength_index_fastDF()
            self.relative_strength_index_slowDF()

        except Exception as ex:
            agentObj.log.error(traceback.format_exc())
