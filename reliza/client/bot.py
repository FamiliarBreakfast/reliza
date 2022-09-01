from random import random
import praw
from core.utils import * # todo: fix
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

	def complete(self, text, args={'max_length': 1024, 'temperature': 1, 'repetition_penalty': 1.2, 'do_sample': True}):
		input_ids = self.tokenizer(text, return_tensors='pt').input_ids # todo: tensorflow
		logger.debug('Completing text for string %s...'%text)
		output = self.model.generate(input_ids, **args)
		output = ''.join(self.tokenizer.batch_decode(output[0]))
		logger.debug('Finished test for string %s: %s'%(text, output))
		return output

class GeneratorParlai(Generator): # im not convinced ill ever add this
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
				response = self.model.complete(uinput) # generate text
				response = remove_garbage(response) # fix garbage generations
				response = fix_trailing_quotes(response)
				response = cut_trailing_sentence(response)
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

		self.reddit = praw.Reddit(
			client_id=self.client_id,
			client_secret=self.client_secret,
			password=self.password,
			username=self.username,
			user_agent="rELIZA Reddit Bot"
		)

	def body(self, submission):
		if type(submission) == praw.models.reddit.submission.Submission:
			return submission.selftext
		elif type(submission) == praw.models.reddit.comment.Comment:
			return submission.body
		else:
			raise Exception('%s not submission.'%type(submission))

	def iterate_through_comments(self, comment):
		tree = []
		i = 0
		while not comment.is_root:
			tree.append(comment.body)
			comment = comment.parent()
			if i == 8:
				break
			i += 1
		tree.append(comment.body)
		tree.reverse()
		return '\n'.join(tree), i # return comment tree and depth of the tree

	def run(self):
		while True:
			for comment in self.reddit.subreddit(self.subreddit).stream.comments(skip_existing=True):
				if not comment.author == self.username: # don't respond to self
					if comment.body is not None: # don't respond to deleted/empty comments
						comment_tree = self.iterate_through_comments(comment) # get comment tree
						if self.classifier.classify(comment.body): # if comment is positive
							response = self.model.complete(comment_tree+'\n') # generate response
							response = response[max(len(comment_tree), response.rfind('\n')+1):] # remove comment tree from response
							response = remove_garbage(response) # fix garbage generations
							response = fix_trailing_quotes(response)
							response = cut_trailing_sentence(response)
							if len(response) > 2:
								comment.reply(response) # post to reddit
								logger.info('Replied to comment %s with %s'%(comment.id, response))
								logger.debug('Comment tree: %s'%comment_tree)
			for submission in self.reddit.subreddit(self.subreddit).stream.submissions(skip_existing=True):
				if not submission.author == self.username: # don't respond to self
					if submission.selftext is not None: # don't respond to deleted/empty submissions
						if self.classifier.classify(submission.selftext): # if submission is positive
							response = self.model.complete(submission.selftext+'\n') # generate response
							response = response[max(len(submission.selftext), response.rfind('\n')+1):] # remove original submission from response
							response = remove_garbage(response) # fix garbage generations
							response = fix_trailing_quotes(response)
							response = cut_trailing_sentence(response)
							if len(response) > 2:
								comment.reply(response) # post to reddit
								logger.info('Replied to submission %s with %s'%(submission.id, response))
								logger.debug('Submission: %s'%submission.selftext)
