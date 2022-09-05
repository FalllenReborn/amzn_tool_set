# by Targosz Seweryn
# tseweryn@amazon.com

import logging
import functools
import traceback

logging.basicConfig(level=logging.INFO,
                    filename='defect_logger/log.log',
                    filemode='w',
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


def defect_logger(func):
    @functools.wraps(func)
    def defect_wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function: {func}. Args: {*args,}")
            return result
        except Exception as e:
            logger.exception(f"Exception raised in {func.__name__}, with args: {*args,}. exception: {str(e)}")
            logger.error(traceback.format_exc())
    return defect_wrapper
