import logging
import os
import sys
sys.path.append(os.getcwd()[:os.getcwd().find("TickAlgoAgent")+len("TickAlgoAgent")])
import shutil
import traceback
from src.main.algo_agent_object import AlgoAgentObjects as agentObj


def setup_custom_logger(name):
    try:
        if not os.path.exists(agentObj.parser.get('common', 'log_path')):
            os.makedirs(agentObj.parser.get('common', 'log_path'))
        else:
            shutil.rmtree(agentObj.parser.get('common', 'log_path'))
            os.makedirs(agentObj.parser.get('common', 'log_path'))
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
        if agentObj.parser.get('common', 'log_level').lower() == "info":
            log_level = logging.INFO
        elif agentObj.parser.get('common', 'log_level').lower() == "debug":
            log_level = logging.DEBUG
        elif agentObj.parser.get('common', 'log_level').lower() == "error":
            log_level = logging.ERROR
        elif agentObj.parser.get('common', 'log_level').lower() == "warn":
            log_level = logging.WARN
        else:
            log_level = logging.INFO
        logfile = agentObj.parser.get('common', 'log_path')+os.sep+"algo_agent.log"
        handler = logging.FileHandler(logfile)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        logger.addHandler(handler)
        return logger
    except Exception as ex:
        logger.error(ex)
        logger.error(traceback.format_exc())
    return None