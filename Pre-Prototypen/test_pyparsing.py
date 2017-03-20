###
# File: test_program.py
# Author: Mailan
# Date: 11.05.16
# Purpose: 
#	1) Read in book title list.
#	2) POS-tag the book titles.  
#	3) Find defined grammar pattern.
#	4) Create statistics about found the grammar pattern in a seperate file.  
###

import csv
import nltk
import re
from nltk import word_tokenize
from pyparsing import Forward, Literal, Group, OneOrMore, ZeroOrMore

#GRAMMAR DEFINITION

#randomletter = ZeroOrMore(Word(alphas))
#NOUN = OneOrMore(NN + randomletter)

NNPS = Literal('NNPS')
NNP = Literal('NNP')
NNS = Literal('NNS')
NN = Literal('NN')

VDB = Literal('VDB')
VBG = Literal('VBG')
VBN = Literal('VBN')
VBP = Literal('VBP')
VBZ = Literal('VBZ')
VB = Literal('VB')

JJ = Literal('JJ')
RB = Literal('RB')
RBR = Literal('RBR')
RBS = Literal('RBS') 

DT = Literal('DT')
AND = Literal('AND')
OF = Literal('OF')
POS = Literal('POS')

NOUN = Group(OneOrMore(NNPS|NNP|NNS|NN))
#PROPER_NOUN = Group(OneOrMore(NNP|NNPS))
VERB = OneOrMore(VDB|VBG|VBN|VBP|VBZ|VB)
ADJECTIVE = OneOrMore(JJ)
ADVERB = OneOrMore(RB)

ARTICLE_NOUN = Group(DT + NOUN)
ADJECTIVE_NOUN = Group(ADJECTIVE + NOUN)
VERB_NOUN = Group(VERB + NOUN)
POS_NOUN = Group((ARTICLE_NOUN | NOUN) + POS + (ADJECTIVE_NOUN | VERB_NOUN | NOUN)) 
ARTICLE_ADJECTIVE_NOUN = Group(DT + ADJECTIVE_NOUN)
NOUN_AND_NOUN = Group((NOUN | ARTICLE_NOUN) + AND + (POS_NOUN | ARTICLE_NOUN | NOUN))
NOUN_OF_NOUN = Group((NOUN_AND_NOUN | ARTICLE_NOUN | NOUN) + OF + (NOUN_AND_NOUN | ARTICLE_NOUN | NOUN))

#TODO
DT.setResultsName('article')
NOUN.setResultsName('noun')

#TODO
expr = Forward()
expr << (NOUN_OF_NOUN | 
		NOUN_AND_NOUN | 
		ARTICLE_ADJECTIVE_NOUN | 
		ADJECTIVE_NOUN | 
		POS_NOUN |
		ARTICLE_NOUN |  
		NOUN)

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
			# change POs tag for 'and' into 'AND'	
			elif token[0] == 'and':
				temp.append('AND')
			else:	
				temp.append(token[1])	
		onlyPOS.append(temp)
	return onlyPOS	

#TODO declare ExceptionError for not found pattern
def search_for_pattern(onlyPOS):
	'''Prints results of found pattern.'''
	pattern_list = [None] * titlelist_length
	
	#find patterns
	for index, title_pos in enumerate(onlyPOS):
		temp_pos = ''
		for pos_index, pos in enumerate(title_pos):	
			#combine POS tag in a sentence
			if pos_index == 0:
				temp_pos = temp_pos + pos
			else:
				temp_pos = temp_pos + ' ' + pos
		pattern_list[index] = (expr.parseString(temp_pos)).asList()
		#pattern_list[index] = (expr.parseString(temp_pos)).asXML('book title')
		
	#print results
	result = [None] * titlelist_length
	for index, pos in enumerate(onlyPOS):
		result[index] = (title_list[index], pos, pattern_list[index])
		print(result[index])
		
		#print pattern_list[index]
		
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