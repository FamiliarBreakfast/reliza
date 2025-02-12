import re

def remove_garbage(text):
	text = text.replace("<|endoftext|>", "")
	re.sub('[^\n -~]', '', text)
	re.sub('(\\.|\t)', '', text)
	return text

def fix_trailing_quotes(text):
    num_quotes = text.count('"')
    if num_quotes % 2 == 0:
        return text
    else:
        return text + '"'

def cut_trailing_sentence(text):
    last_punc = max(text.rfind("."), text.rfind("!"), text.rfind("?"), text.rfind(".\""), text.rfind("!\""), text.rfind("?\""), text.rfind(".\'"), text.rfind("!\'"), text.rfind("?\'"))#todo: regexify
    if last_punc <= 0:
        last_punc = len(text) - 1
    et_token = text.find("<")
    if et_token > 0:
        last_punc = min(last_punc, et_token - 1)
    text = text[: last_punc + 1]
    return text

def strip_negative_keywords(text, keywords):
	for key in list(keywords):
		if key in text:
			text = text.replace(key, keywords.get(key))
	return text