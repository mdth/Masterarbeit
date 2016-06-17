###
# File: test_program.py
# Author: Mailan
# Date: 08.05.16
# Purpose: 
#	1) Read in book title list.
#	2) POS-tag the book titles.  
#	3) Find defined regex pattern.
#	4) Create statistics about found the regex pattern in a seperate file.  
###

import csv
import nltk
import re
from nltk import word_tokenize

# pattern
NOUN = re.compile('(NNS|NNP|NN)+(?!\w)')
ARTICLE_NOUN = re.compile('DT(NNS|NNP|NN)+(?!\w)')
ADJECTIVE_NOUN = re.compile('(DT)*(JJ)+(NNS|NNP|NN)+(?!\w)')
X_OF_Y = re.compile('(\w)+OF(\w)+')
FOR = re.compile('(\w)+IN(\w)+')
AND = re.compile('(NNS|NNP|NN)+AND(DT)*(NNS|NNP|NN)+(POS)*(NNS|NNP|NN)*')
VERB = re.compile('(VDB|VBG|VBN|VBP|VBZ|VB)+(?!\w)')
ADVERB = re.compile('RB(?!\w)+')
DATE = re.compile('CD(?!\w)+')

def read_in_file():
	"""Returns read in csv file(s)."""
	title_list = []
	with open('C:/Users/din_m/Desktop/MA/booklist+.csv', 'rb') as f:
		reader = csv.reader(f, delimiter=';')
		for row in reader:
			title_list.append(row[0])
	return title_list;		


def tokenize_and_POS_tagging(title_list):
	"""Returns tokenized title list and POS tagged token list."""
	title_list_tokens = []
	title_list_POS = []
	for title in title_list:
		tokens = word_tokenize(title)
		title_list_tokens.append(tokens)
		title_list_POS.append(nltk.pos_tag(tokens))
	return title_list_tokens, title_list_POS

def get_POS_only(title_list_POS):
	"""Returns a list of the POS tags. POS tag for the word 'of' will be changed to 'OF'."""
	onlyPOS = []
	for title in title_list_POS:
		temp = []
		for token in title:
		
			# change POS tag for 'of' into 'OF'
			if token[0] == 'of':
				temp.append('OF')
			# change POS tag for 'and' into 'AND'	
			elif token[0] == 'and':
				temp.append('AND')	
			else:	
				temp.append(token[1])
				
		onlyPOS.append(temp)
	return onlyPOS	

def search_for_pattern(onlyPOS):
	'''Prints results of found pattern.'''
	pattern_list = [None] * titlelist_length

	# find patterns
	for index, title_pos in enumerate(onlyPOS):
		temp_pos = ''
		for pos_index, pos in enumerate(title_pos):	
			temp_pos = temp_pos + pos
		
		if re.match(NOUN, temp_pos):
			pattern_list[index] = 'NOUN'
		elif re.match(VERB, temp_pos):
			pattern_list[index] = 'VERB'
		elif re.match(ADVERB, temp_pos):
			pattern_list[index] = 'ADVERB'
		elif re.match(ARTICLE_NOUN, temp_pos):
			pattern_list[index] = 'ARTICLE_NOUN'
		elif re.match(ADJECTIVE_NOUN, temp_pos):
			pattern_list[index] = 'ADJECTIVE_NOUN'
		elif re.match(X_OF_Y, temp_pos):
			pattern_list[index] = 'X_OF_Y'
		elif re.match(AND, temp_pos):
			pattern_list[index] = 'AND'	
		elif re.match(FOR, temp_pos):
			pattern_list[index] = 'FOR'		
		else:
			None

	#print results
	result = [None] * titlelist_length
	for index, pos in enumerate(onlyPOS):
		result[index] = (title_list[index], pos, pattern_list[index])
		
	for row in result:	
		print row	

#def write_results_into_csv(result):
#	'''Writes the results in a csv file.'''
#	with open('C:/Users/din_m/Desktop/MA/booklist_tags.csv', 'wb') as csvfile:
#	    writer = csv.writer(csvfile, delimiter=';')
#			for item in result:
#				writer.writerow(item[0] + ';' + item[1] + ';' + item[2])


title_list = read_in_file()
titlelist_length = len(title_list)
title_list_tokens, title_list_POS = tokenize_and_POS_tagging(title_list)
onlyPOS = get_POS_only(title_list_POS)
search_for_pattern(onlyPOS)	