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
		if config['task'] == 'one-on-one':
			if config['client']['platform'] == 'terminal':
				bot = TerminalBot(
								name=config['name'],
								provider=config['provider']['platform'],
									tokenizer=config['provider']['tokenizer'],
									model=config['provider']['model'],
									#args=config['provider']['args']
								)
				logger.info('Starting %s with the terminal as the client...'%config['name'])
				bot.run()
		elif config['task'] == 'classification':
			if config['client']['platform'] == 'terminal':
				bot = TerminalClassifierBot(
								name=config['name'],
								provider=config['provider']['platform'],
									tokenizer=config['provider']['tokenizer'],
									model=config['provider']['model'],
									#args=config['provider']['args'],
								classifier=config['classifier']['model'],
									interests=config['classifier']['interests'],
									detests=config['classifier']['detests']
								)
				logger.info('Starting %s with the terminal as the client...'%config['name'])
				bot.run()
		elif config['task'] == 'conversational':
			if config['client']['platform'] == 'reddit':
				bot = RedditBot(
								name=config['name'],
								provider=config['provider']['platform'],
									tokenizer=config['provider']['tokenizer'],
									model=config['provider']['model'],
									#args=config['provider']['args'], sort this shit out later
								subreddit=config['client']['subreddit'],
								client_id=config['client']['auth']['client_id'],
								client_secret=config['client']['auth']['client_secret'],
								username=config['client']['auth']['username'],
								password=config['client']['auth']['password'],
									frequency=config['client']['post']['frequency'],
									flair=config['client']['post']['flair'],
									type=config['client']['post']['type'],
									img_backend=config['client']['post']['img_backend'],
								classifier=config['classifier']['model'],
									interests=config['classifier']['interests'],
									detests=config['classifier']['detests']
								)
				logger.info('Starting %s with the reddit client...'%config['name'])
				bot.run()
			else:
				raise Exception('unsupported client')
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
