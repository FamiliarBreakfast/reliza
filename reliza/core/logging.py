import os
import time
import logging

# check if log directory exists
if not os.path.exists('logs'):
	os.makedirs('logs')

logging.basicConfig(level=logging.INFO,
					format='[%(asctime)s] %(levelname)s: %(message)s',
					handlers=[logging.FileHandler(f'logs/{time.strftime("%Y-%m-%d_%H-%M-%S")}.log'),logging.StreamHandler()])

def get_logger(name):
	return logging.getLogger(name)