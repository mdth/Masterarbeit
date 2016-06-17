###
# File: test_program.py
# Author: Mailan
# Date: 22.05.16
# Purpose: 
#	1) Read in rdf file.
#	2) Find pattern from rdf.  
#	3) Search pattern in some text with regex.
#	4) Create statistics about found the grammar pattern in a seperate file.  
###

import nltk
import re
from nltk import word_tokenize
from pyparsing import alphas, dblQuotedString, Forward, Literal, Group, OneOrMore, Optional, removeQuotes, Suppress, Word

#GRAMMAR DEFINITION

word = prefix = suffix = Word(alphas) 
COLON = Literal(':')
#BSCALE = Literal('BScale')
#BSORT = Literal('BSort')
#OBJECT = Literal('Object')
#VOCABULARY = Literal('Vocabulary')
#HASPATTERN = Literal('hasPattern')
#HASATTRIBUTE = Literal('hasAttribute')
A = Literal('a')
QUOTEDSTRING = dblQuotedString.setParseAction(removeQuotes)

# suppressing following literals 
LPAREN = Suppress('(')
RPAREN = Suppress(')')
DOT = Suppress('.')
COMMA = Suppress(',')
SEMICOLON = Suppress(';')

GETSUFFIX = Suppress(prefix + COLON) + suffix
GETOBJECT = Optional(LPAREN) + OneOrMore((GETSUFFIX | QUOTEDSTRING) + Optional(COMMA)) + Optional(RPAREN)

isA = (GETSUFFIX('subject')| word ) + A('relation') + GETSUFFIX('object') + DOT
hasX = GETSUFFIX('subject') + GETSUFFIX('relation') + Group(GETOBJECT)('object') + DOT

search = Forward()
search << (isA | hasX)

def read_in_file(filename):
	with open(filename, 'rb') as file:
		return file.read()

def read_in_rdf_file(filename):
	"""Returns read in rdf file(s)."""
	cleaned_rdf = []
	with open(filename, 'rb') as file:
		data = file.read()
		rdf_data = data.splitlines()
		for data in rdf_data:
			if data != '':
				cleaned_rdf.append(data)
		return cleaned_rdf
		
def get_pattern_from_RDF(data):
	"""Returns only pattern list from RDF data."""
	#TODO debug print
	print "Found pattern in RDF."
	
	pattern_list = dict()
	for statements in data:
		has_pattern = ' has pattern: '
		parserResult = search.parseString(statements)
		subject, relation, object = parserResult
		if relation == 'hasPattern':
			pattern_list.update({subject : object})
			#TODO debug line		
			print "%s %s %s" % (subject, has_pattern, object)				
	return pattern_list		

def compile_pattern(string):
	'''Compile a found pattern to search for it in text.'''
	return re.compile(string)

def search_pattern(pattern, found_pattern, text):
	'''Searches for the pattern found in the rdf in some text. Returns the number of found instances in the text.'''
	# add ignorecase?
	search_pattern = compile_pattern('(\s)?' + pattern + '(\s|\.|,)')
	return len(re.findall(search_pattern, text))
	
def search_for_pattern(text, rdf_pattern):
	'''Prints results of number of found RDF key in random text.'''
	found_pattern = dict()
	#find key
	for key in rdf_pattern:
		pattern = rdf_pattern[key]
		found_pattern[key] = 0
		# object only has one key
		if len(pattern) == 1:
			found_pattern.update({key : search_pattern(pattern[0], found_pattern, text)})
		# object has more than one key
		else:
			num_matches = 0
			for item in pattern:
				num_matches = num_matches + search_pattern(item, found_pattern, text)
			found_pattern.update({key : num_matches})	
	#TODO debug print
	print "Found pattern in text:"
	print found_pattern			

data = read_in_rdf_file('C:/Users/din_m/Google Drive/MA/Prototypen/vhs_qcalculus_mod.rdf')
parsed_RDF = get_pattern_from_RDF(data)
text = read_in_file('C:/Users/din_m/Google Drive/MA/Prototypen/test.txt')
search_for_pattern(text, parsed_RDF)