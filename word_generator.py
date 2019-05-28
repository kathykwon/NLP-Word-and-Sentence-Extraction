"""
Kathy Kwon
"""
import os
import nltk
import csv
import argparse
import re
import pdb
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

DOC_LIST = ["doc1.txt", "doc2.txt", "doc3.txt", "doc4.txt", "doc5.txt", "doc6.txt"]
DEFAULT_NUM = 20

def _get_wordnet_pos(word):
	"""
	Source: Machine Learning Plus
	Lemmatize with POS Tag
	Map POS tag to first character lemmatize() accepts
	"""
	tag = nltk.pos_tag([word])[0][1][0].upper()
	tag_dict = {
		"J": wordnet.ADJ,
		"N": wordnet.NOUN,
		"V": wordnet.VERB,
		"R": wordnet.ADV,
	}
	return tag_dict.get(tag, wordnet.NOUN)


def _get_all_tokens(doc_list):
	"""
	Reads in all given documents and maps all the words and sentences to their 
	respective documents
	
	Parameters:
		doc_list: list of documents the user wants to scan

	Returns: 
		word_tokens: documents mapped to a list of (unfiltered) words that appear
		sent_tokens: list of all sentences
	"""
	word_tokens, sent_tokens = {}, []
	for doc in doc_list:
		with open(doc, "r", encoding="utf-8") as fo:
			output = fo.read()
			words = nltk.word_tokenize(output)  			# Splits into list of words
			sent_tokens.extend(nltk.sent_tokenize(output))  # Splits into list of sentences
		word_tokens[doc] = words
	return word_tokens, sent_tokens


def _filter_words(word_tokens):
	"""
	Filters out all stop words and certain parts of speech that do not tell much 
	about the given corpus
	
	Parameters:
		word_tokens: dict of docs to list of words (unfiltered)

	Returns:
		filtered_words_dict: dict of docs to list of words (filtered)
		lemma_to_original: dict of lemmatized words mapped to original words
	"""
	wnl = WordNetLemmatizer()
	filtered_words_dict = {}
	lemma_to_original = {}
	included_pos = set([
		"FW", 							# Foreign words
		"JJ", "JJR","JJS",				# Adjectives
		"NN", "NNS", "NNP", "NNPS", 	# Nouns
		"RBR", "RBS", 					# Adverbs
		"VB", "VBG", "VBN"				# Verbs
	])
	for doc, unfiltered_words in word_tokens.items():
		filtered_words = []
		pos_tup_list = nltk.pos_tag(unfiltered_words)	# [(word, pos), ...]
		for tup in pos_tup_list:
			word, pos = tup
			if pos in included_pos:
				filtered_words.append(wnl.lemmatize(word, _get_wordnet_pos(word)))
				lemma_to_original[wnl.lemmatize(word, _get_wordnet_pos(word))] = word
		filtered_words_dict[doc] = filtered_words	
	return filtered_words_dict, lemma_to_original


def _count_tokens(filtered_words_dict, num):
	"""
	Counts the occurences of words, and sorts them from most frequent to least frequent
	
	Parameters:
		filtered_words_dict: dict of docs to filtered words
		num: number of words the user wants to output onto .csv file
	
	Returns:
		word_freq_list: a list of tuples (word, freq) of the num most frequently used words
	"""
	all_word_tokens = []
	for doc, words in filtered_words_dict.items():
		all_word_tokens.extend(words)
	c = Counter(all_word_tokens)
	if num > len(all_word_tokens): 		# Error handling
		print("Desired number of words exceeds number of words in document. Scanning all words instead.")	
		num = len(all_word_tokens)
	word_freq_list = c.most_common(num)
	return word_freq_list


def _get_pos_list(word_freq_list):
	"""
	Uses WordNet categorization of the part of speech of the most frequently used 
	words

	Parameters:
		word_freq_list: a list of tuples (word, freq) of the num most frequently used words

	Returns: 
		pos_list: a list of part of speech of the passed in words
	"""
	pos_list = []
	for tup in word_freq_list:
		word, freq = tup
		wordnet_pos = _get_wordnet_pos(word)
		if wordnet_pos == "a":
			pos_list.append("adjective")
		elif wordnet_pos == "r":
			pos_list.append("adverb")
		elif wordnet_pos == "v":
			pos_list.append("verb")
		else:
			pos_list.append("noun")
	return pos_list


def _get_doc_list(filtered_words_dict, word_freq_list):
	"""
	Searches through documents and tracks documents for which a frequently
	used word appears
	
	Parameters:
		filtered_words_dict: dict of docs to filtered words
		word_freq_list: a list of tuples (word, freq) of the num most frequently used words

	Returns:
		doc_list: a list of lists of documents for all frequently used words
	"""
	doc_list = []			# list of lists of doc for which a word appears
	for word, freq in word_freq_list:
		word_docs = []		# a single list of all docs for which one word appears
		for doc, filtered_words_list in filtered_words_dict.items():
			if word in filtered_words_list:
				word_docs.append(doc)
		doc_list.append(word_docs)
	return doc_list


def _get_sent_list(word_freq_list, sent_tokens, lemma_to_original):
	"""
	Get up to three sentences that each most frequently used word is used in
	
	Parameters:
		word_freq_list: a list of tuples (word, freq) of the num most frequently used words
		sent_tokens: list of all sentences
		lemma_to_original: dict of lemmatized words mapped to original words

	Returns:
		sent_list: a list of lists of up to 3 sentences per word
	"""
	sent_list = [] 		# list of list of sentences
	for tup in word_freq_list:
		word, freq = tup
		sents = []		# list of list containing group of 1 to 3 sentences in each list value
		for sent in sent_tokens:
			if lemma_to_original[word] in re.split(r"[^\w'-]+", sent) or word in re.split(r"[^\w'-]+", sent):
				sents.append(sent)
			if len(sents) == 3:
				break
		sent_list.append(sents)
	return sent_list


def _write_data(word_freq_list, doc_list, pos_list, sent_list):
	"""
	Creates a .csv file with the following data:
		Word, frequency, part of speech, document(s), sentence(s)

	Parameters:
		word_freq_list: a list of tuples (word, freq) of the num most frequently used words
		doc_list: a list of lists of documents for all filtered words
		pos_list: a list of part of speech of the passed in words
		sent_list: a list of lists of up to 3 sentences per word
	"""
	headers = [
		"Words (#)",
		"Frequency",
		"Part of Speech",
		"Document(s)",
		"Sentence(s) containing the word",
	]
	with open("most_common_words.csv", "w", newline="") as csvfile:
		writer = csv.writer(csvfile, delimiter=",")
		writer.writerow(headers)
		for i, tup in enumerate(word_freq_list):
			word, freq = tup
			pos = pos_list[i]
			docs = ", ".join(doc_list[i])
			sentence = "\n\n".join(sent_list[i])
			row = [word, freq, pos, docs, sentence]
			writer.writerow(row)


def _process_args():
	"""
	Parses and processes args.
	The user has ability to pass in documents and number of desired words

	Returns:
		args: arguments that the user passes
	"""
	parser = argparse.ArgumentParser(description="Please enter list of documents to scan and number of words to output.")
	parser.add_argument("--doc", help="Flag for entering documents.", nargs="+", dest="doc")
	parser.add_argument("--num", help="Flag for entering number of words.", type=int, dest="num")
	args = parser.parse_args()
	if args.doc is None:  # If no flag is passed in, automatically call test documents
		print("No documents passed; using sample documents: doc1.txt, doc2.txt, doc3.txt, doc4.txt, doc5.txt, doc6.txt")
		args.doc = DOC_LIST
	if args.num is None:
		print("No number of words passed, using default number: 20")
		args.num = DEFAULT_NUM
	return args


if __name__ == "__main__":
	"""
	Main function parses arguments
	Calls write_data function, and generates .csv file
	"""
	args = _process_args()

	print("Running... Please do not exit...")

	word_tokens, sent_tokens = _get_all_tokens(args.doc)
	filtered_words_dict, lemma_to_original = _filter_words(word_tokens)
	word_freq_list = _count_tokens(filtered_words_dict, args.num)
	pos_list = _get_pos_list(word_freq_list)
	doc_list = _get_doc_list(filtered_words_dict, word_freq_list)
	sent_list = _get_sent_list(word_freq_list, sent_tokens, lemma_to_original)

	# Generates .csv file
	_write_data(word_freq_list, doc_list, pos_list, sent_list)
	print("Success! The file 'most_common_words.csv' has been created!")