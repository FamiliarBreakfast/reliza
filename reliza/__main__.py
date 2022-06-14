from core.logging import get_logger
from client.bot import TerminalBot, TerminalClassifierBot, RedditBot

import sys
import json
import traceback
import argparse

logger = get_logger(__name__)

##Deprecated
#def get_key(dictionary, key, required=True, default=None):
#	if key in dictionary:
#		return dictionary[key]
#	elif required:
#		raise Exception(f'{key} is required')
#	else:
#		return default

def parse():
	parser = argparse.ArgumentParser(
		description="rELIZA is a configurable open-domain chatbot.",
		usage="reliza [arguments]",
	)
	parser.add_argument(
		'-c', '--config',
		help="Path to the config file.",
		type=str,
		required=True
	)
	return parser.parse_args()

def load(args):
	with open(args.config, encoding='utf-8') as f:
		return json.load(f)

def main():
	logger.info('Initializing rELIZA...')
	logger.info('Loading config...')
	config = load(parse())
	bot = None
	exit_code = 0
	try:
		if 'terminal' in config['client']:
			if config['client']['terminal']['task'] == 'one-on-one':
				bot = TerminalBot(
					task=config['client']['terminal']['task'],
					mode=config['client']['classifier']['mode'],
					platform=config['client']['generation']['platform'],
						tokenizer=config['client']['generation']['tokenizer'],
						model=config['client']['generation']['model'],
						#args=config['client']['generation']['args']
				)
				bot.run()
			if config['client']['terminal']['task'] == 'classification':
				bot = TerminalClassifierBot(
					task=config['client']['terminal']['task'],
					mode=config['client']['classifier']['mode'], classifier=config['client']['classifier']['model'],
						interests=config['client']['classifier']['interests'],
						detests=config['client']['classifier']['detests'],
					platform=config['client']['generation']['platform']
				)
				bot.run()
			if config['client']['reddit']['task'] == 'discussion':
				raise NotImplementedError('task discussion not supported for terminal client.')
		elif 'reddit' in config['client']:
			if config['client']['reddit']['task'] == 'one-on-one':
				raise NotImplementedError('One-on-one reddit bot is not supported yet.')
			if config['client']['reddit']['task'] == 'classification':
				#bot = DebugClassificationBot()
				raise Exception('Classification reddit bot is not supported yet.')
			if config['client']['reddit']['task'] == 'discussion':
				bot = RedditBot(
					task=config['client']['reddit']['task'],
					subreddit=config['client']['reddit']['subreddit'],
						client_id=config['client']['reddit']['client_id'],
						client_secret=config['client']['reddit']['client_secret'],
						username=config['client']['reddit']['username'],
						password=config['client']['reddit']['password'],
					mode=config['client']['classifier']['mode'], classifier=config['client']['classifier']['model'],
						interests=config['client']['classifier']['interests'],
						detests=config['client']['classifier']['detests'],
					platform=config['client']['generation']['platform'],
						tokenizer=config['client']['generation']['tokenizer'],
						model=config['client']['generation']['model'],
						#args=config['client']['generation']['args']
				)
				bot.run()
		else:
			#todo: user clients
			raise Exception('No valid client.')
	except KeyboardInterrupt:
		print('Exiting...')
		exit_code = 0
	except Exception as e:
		logger.error(e)
		logger.error(traceback.format_exc())
		exit_code = 1
	finally:
		logger.info('Exiting...')
		sys.exit(exit_code)

if __name__ == '__main__':
	main()
