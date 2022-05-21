#from shimeji.model_provider import ModelProvider, Sukima_ModelProvider, ModelGenRequest, ModelGenArgs, ModelSampleArgs, ModelLogitBiasArgs, ModelPhraseBiasArgs
#from shimeji.memorystore_provider import MemoryStoreProvider, PostgreSQL_MemoryStoreProvider
from .logging import get_logger
import argparse
import json

logger = get_logger('args')

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

def config(args):
	with open(args.config, encoding='utf-8') as f:
		return json.load(f)

def get_item(obj, key):
	if key in obj:
		return obj[key]
	else:
		return None

#def get_memorystore_provider(args):#not essential? hopefully
#	if 'memory_store' not in args:
#		logger.warning('running without memory store -- the chatbot will not be able to remember anything')
#		return None, None
#	
#	if 'database_type' in args['memory_store']:
#		if args['memory_store']['database_type'] == 'postgresql':
#			return PostgreSQL_MemoryStoreProvider(
#				database_uri=args['memory_store']['database_uri']
#			), {
#				'model': args['memory_store']['model'],
#				'model_layer': args['memory_store']['model_layer'],
#				'short_term_amount': args['memory_store']['short_term_amount'],
#				'long_term_amount': args['memory_store']['long_term_amount'],
#			}
#		else:
#			raise Exception('database_type is not supported.')
#	else:
#		raise Exception('memory_store requires database_type to be specified.')

def get_vision_provider(args):
	if 'vision_provider' not in args:
		return None
	
	return args['vision_provider']

def get_model_provider(args):
	# load model provider gen_args into basemodel
	if 'model_provider' not in args:
		raise Exception('model_provider is not specified in config file.')
	if args["model_provider"]["name"] == "sukima":
		raise Exception('sukima is not supported.')
	if args["model_provider"]["name"] == "huggingface" or args["model_provider"]["name"] == "transformers":
		pass
	if args["model_provider"]["name"] == "parlai":
		pass
	else:
		raise Exception('model_provider is not supported.')
