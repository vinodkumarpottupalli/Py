import os
import time
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger("my_streamlit_logger")

def process():
    logger.info("Started Execution")
    time.sleep(5)
    logger.info("Execution stopped after 5 sec!!")
    return True

def read_data():
    data = pd.DataFrame(
        np.random.randn(50, 5),
        columns=[f"col {i}" for i in range(5)]
        ).to_csv().encode('utf-8')
    return data