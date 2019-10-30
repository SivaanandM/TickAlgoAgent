import sys,os
sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
from src.main.algo_agent_object import AlgoAgentObjects as abObj


class SapmObjects():

    SYMBOL = abObj.symbol
    TI = int(abObj.parser.get('sapm', 'TI'))
    DTH = float(abObj.parser.get('sapm', 'DTH'))
    TSL = 0.0 #float(abObj.parser.get('sapm', 'TSL'))
    SL = 0.0 #float(abObj.parser.get('sapm', 'SL'))
    titicks = []
    # this list we are going to save time interaval ticks
    avgs = []

    LBuy_Position = False  # Long buy position
    SSell_Position = False  # Short sell position
    LSL_Price = 0  # Long buy stop loss
    SSL_Price = 0  # Shotsell stop loss
    LB_Price = 0  # long buy Price
    SS_Price = 0  # short sell Price
    No_Trades = 0

    LSL_Price = 0
    # Long buy stop loss
    SSL_Price = 0
    # Shot sell stop loss

    TI_SAPM_LONG = 0
    TI_SAPM_SHORT = 0

    net_profit = []


