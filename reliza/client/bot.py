from core.logging import get_logger
logger = get_logger(__name__)

class Generator:
	def __init__(self, platform, tokenizer, model):
		self.platform = platform
		self.tokenizer = tokenizer
		self.model = model

		if self.platform == 'sukima':
			raise Exception('sukima is not supported. Use eliza instead.')
		elif self.platform == 'huggingface' or self.platform == 'transformers':
			logger.info('Using huggingface model provider...')
			if model in ['gpt', 'gpt2', 'gpt-neo', 'gpt-j', 'gpt-neo-x']:
				from transformers import AutoTokenizer, AutoModelForCausalLM
				self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
				self.model = AutoModelForCausalLM.from_pretrained(model)
			else:
				raise NotImplementedError('Model %s is not supported. Raise github issue.'%model)
		elif self.platform == 'parlai':
			logger.info('Using parlai model provider...')
			raise NotImplementedError('parlai is not supported yet.')
		else:
			raise Exception('Platform %s is not supported. Raise github issue.'%self.platform)

class Conversational(Generator):
	def generate(self, text, args={'max_length': 128, 'temperature': 0.7, 'do_sample': True}):
		if self.platform == 'sukima':
			raise Exception('sukima is not supported. Use eliza instead.')
		if self.platform == 'huggingface' or self.platform == 'transformers':
			input_ids = self.tokenizer(text, return_tensors='pt').input_ids #todo: tensorflow
			logger.debug('Completing text for string %s...'%text)
			output = self.model.generate(input_ids, **args)
			output = ''.join(self.tokenizer.batch_decode(output[0]))
			logger.debug('Finished test for string %s: %s'%(text, output))
			return output
		if self.platform == 'parlai':
			raise NotImplementedError('parlai is not supported yet.')
		else:
			raise Exception('Platform %s is not supported. Raise github issue.'%self.platform)

class Bot:
	def __init__(self, name, task, provider, **kwargs):
		self.name = name
		self.task = task
		self.provider = provider
		self.kwargs = kwargs
	
	def run(self):
		raise NotImplementedError

class TerminalBot(Bot):
	def __init__(self, name, **kwargs):
		self.model = Conversational(kwargs['provider'], kwargs['tokenizer'], kwargs['model'])
	def run(self):
		while True:
			try:
				uinput = input("Write something: ")
				print(uinput)
				response = self.model.generate(uinput)
				print(response)
			except KeyboardInterrupt:
				print('\nBye!')
				break

class RedditBot(Bot):
	def __init__(self, name, **kwargs):
		pass
	pass