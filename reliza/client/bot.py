from random import random
from xml.dom import NotSupportedErr
import praw
from core.logging import get_logger
logger = get_logger(__name__)

class Generator:
	def __init__(self, platform):
		self.platform = platform # this is stupid but i might use it in the future

class GeneratorHuggingface(Generator):
	def __init__(self, platform, tokenizer, model):
		super().__init__(platform)
		self.tokenizer = tokenizer
		self.model = model

		if 'gpt' in model:
			logger.info('Using GPT transformer...') # todo: stuff
		elif 'bert' in model:
			logger.info('Using BERT transformer...')
		else:
			logger.info('Using custom transformer...')

		from transformers import AutoTokenizer, AutoModelForCausalLM
		self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
		self.model = AutoModelForCausalLM.from_pretrained(model)

	def complete(self, text, args={'max_length': 128, 'temperature': 0.7, 'do_sample': True}):
		input_ids = self.tokenizer(text, return_tensors='pt').input_ids # todo: tensorflow
		logger.debug('Completing text for string %s...'%text)
		output = self.model.generate(input_ids, **args)
		output = ''.join(self.tokenizer.batch_decode(output[0]))
		logger.debug('Finished test for string %s: %s'%(text, output))
		return output

class GeneratorParlai(Generator):
	pass # pylance freaks out if i put an exception here

class Classifier():
	def classify(self):
		return True

class ZeroShot(Classifier):
	def __init__(self, model=None, interests=['positive'], detests=['negative']):
		self.model = model
		self.interests = interests
		self.detests = detests
	
	def classify(self, text, **kwargs):
		if self.model == None:
			raise Exception('No model specified.')
		else:
			from transformers import pipeline
			classifier = pipeline("zero-shot-classification", self.model)
			sequence = text
			logger.debug('Classifying interests for string %s...'%sequence)
			interest_prob = classifier(sequence, self.interests, multi_label=True)
			logger.debug(interest_prob['scores'])
			logger.debug('Classifying detests for string %s...'%sequence)
			detest_prob = classifier(sequence, self.detests, multi_label=True)
			logger.debug(detest_prob['scores'])
			rand = random()
			if 'return_prob' in kwargs and kwargs['return_prob']:
				if 'return_rand' in kwargs and kwargs['return_rand']:
						return interest_prob, detest_prob, rand
				else:
					return interest_prob, detest_prob
			if sum(detest_prob['scores']) > sum(interest_prob['scores']):
				return False
			elif sum(interest_prob['scores']) > rand:
				return True
			else:
				return False

class Bot:
	def __init__(self, task, mode, platform, **kwargs):
		self.kwargs = kwargs
		self.task = task

		self.mode = mode
		if mode == 'none':
			self.classifier = Classifier()
		if mode == 'zero-shot':
			self.classifier = ZeroShot(kwargs['classifier'], kwargs['interests'], kwargs['detests'])

		self.platform = platform
		if self.platform == 'sukima':
			raise NotImplementedError('sukima is not supported. Use eliza instead.') # im pretty sure im using NotImplementedError wrong, is that bad?
		elif self.platform == 'huggingface' or platform == 'transformers':
			logger.info('Using huggingface model provider...')
			self.model = GeneratorHuggingface(self.platform, kwargs['tokenizer'], kwargs['model'])
		elif self.platform == 'parlai':
			logger.info('Using parlai model provider...')
			raise NotImplementedError('parlai is not supported yet. Please wait patiently.')
		elif self.platform == 'none':
			logger.info('Using None model provider. Text generation will be disabled.')
		else:
			raise Exception('Platform %s is not supported. Raise github issue.'%self.platform)
	
	def run(self):
		raise NotImplementedError

class TerminalBot(Bot):
	def run(self):
		while True:
			try:
				uinput = input("Write something: ")
				response = self.model.complete(uinput)
				print(response)
			except KeyboardInterrupt:
				print('\nBye!')
				break

class TerminalClassifierBot(Bot):
	def run(self):
		while True:
			try:
				uinput = input("Write something: ")
				probability = self.classifier.classify(uinput, return_prob=True, return_rand=True)
				print("Raw probabilities: ", probability)
				tf = self.classifier.classify(uinput)
				print("Would respond: ", tf)
			except KeyboardInterrupt:
				print('\nBye!')
				break

class RedditBot(Bot):
	def __init__(self, task, mode, platform, subreddit, client_id, client_secret, username, password, **kwargs):
		super().__init__(task, mode, platform, **kwargs)
		self.subreddit = subreddit
		self.client_id = client_id
		self.client_secret = client_secret
		self.username = username
		self.password = password

	def poll(self):
		reddit = praw.Reddit(
			client_id=self.client_id,
			client_secret=self.client_secret,
			password=self.password,
			username=self.username,
			user_agent="rELIZA Reddit Bot"
		)

		for comment in reddit.subreddit(self.subreddit).stream.comments(skip_existing=True):
			return comment

	def run(self):
		while True:
			comment = self.poll()
			if comment.body is not None:
				if self.classifier.classify(comment.body):
					response = self.model.complete(comment.body)
					response = response[len(comment.body):]
					if response is not None:
						comment.reply(response)
						logger.info('Replied to comment %s with %s'%(comment.id, response))
