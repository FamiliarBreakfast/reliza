from difflib import SequenceMatcher

def anti_spam(messages, threshold=0.8):#98% sure we dont need this
    to_remove = []
    for i in range(len(messages)):
        for j in range(i+1, len(messages)):
            if i != j:
                if SequenceMatcher(None, messages[i].content, messages[j].content).ratio() > threshold:
                    to_remove.append(j)
    to_remove = list(set(to_remove))
    messages = [messages[i] for i in range(len(messages)) if i not in to_remove]
    return messages, len(to_remove)

def standardize_punctuation(text):
    text = text.replace("’", "'")
    text = text.replace("`", "'")
    text = text.replace("“", '"')
    text = text.replace("”", '"')#todo: regexify
    return text

def remove_garbage(text):
	text = text.replace("\\n", "")
	text = text.replace("\t", "")
	text = text.replace("\r", "")
	text = text.replace("\b", "")
	text = text.replace("\f", "")
	text = text.replace("\v", "")
	text = text.replace("\u200b", "")
	text = text.replace("<|endoftext|>", "")
	return text

def fix_trailing_quotes(text):#optimize
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