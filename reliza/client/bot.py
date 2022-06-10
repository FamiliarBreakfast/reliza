from random import random
import praw
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
				logger.info('Using default GPT model...')
				from transformers import AutoTokenizer, AutoModelForCausalLM
				self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
				self.model = AutoModelForCausalLM.from_pretrained(model)
			else:
				logger.info('Using user-defined transformer...')
				from transformers import AutoTokenizer, AutoModelForCausalLM
				self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
				self.model = AutoModelForCausalLM.from_pretrained(model)
		elif self.platform == 'parlai':
			logger.info('Using parlai model provider...')
			raise NotImplementedError('parlai is not supported yet. please wait patiently.')
		else:
			raise Exception('Platform %s is not supported. Raise github issue.'%self.platform)

class Conversational(Generator):
	def complete(self, text, args={'max_length': 128, 'temperature': 0.7, 'do_sample': True}):
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

class Classifier():
	def __init__(self, model=None, interests=None, detests=None):
		self.model = model
		self.interests = interests
		self.detests = detests

	def classify(self, text, return_prob=False):
		if self.model == None:
			logger.debug('No classifier is specified. Using mode echo...')
		else:
			from transformers import pipeline
			classifier = pipeline("zero-shot-classification", self.model)
			sequence = text
			logger.debug('Classifying interests for string %s...'%sequence)
			interest_prob = classifier(sequence, self.interests, multi_label=True)
			logger.debug('Classifying detests for string %s...'%sequence)
			detest_prob = classifier(sequence, self.detests, multi_label=True)
			if return_prob:
				return interest_prob, detest_prob
			else:
				if sum(detest_prob['scores']) > sum(interest_prob['scores']):
					return False
				elif sum(interest_prob['scores']) > random():
					return True
				else:
					return False

class Bot:
	def __init__(self, name, provider, tokenizer, model, classifier, interests, detests):
		self.name = name

		self.model = Conversational(provider, tokenizer, model)
		self.classifier = Classifier(classifier, interests, detests)
	
	def run(self):
		raise NotImplementedError

class TerminalBot(Bot):
	def run(self):
		while True:
			try:
				uinput = input("Write something: ")
				print(uinput)
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
				print(uinput)
				probability = self.classifier.classify(uinput, return_prob=True)
				print("Raw probabilities: ", probability)
				tf = self.classifier.classify(uinput)
				print("Would respond: ", tf)
			except KeyboardInterrupt:
				print('\nBye!')
				break

class RedditBot(Bot):
	def __init__(self, name, provider, tokenizer, model, classifier, interests, detests, subreddit, client_id, client_secret, username, password, flair=None, frequency=24, type="text", img_backend=None):
		super(RedditBot, self).__init__(name, provider, tokenizer, model, classifier, interests, detests)
		self.subreddit = subreddit
		self.client_id = client_id
		self.client_secret = client_secret
		self.username = username
		self.password = password

		self.flair = flair
		self.frequency = frequency
		self.type = type
		self.img_backend = img_backend

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