class Bot:
    def __init__(self, name, model_provider, **kwargs):
        self.name = name
        self.model_provider = model_provider
        self.kwargs = kwargs
    
    def run(self):
        raise NotImplementedError

class RedditBot(Bot):
	pass