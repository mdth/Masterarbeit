from PMI.Parser import Parser

parser = Parser()

text = parser.nlp('"Ja, ich habe ein Anliegen, ...", begann der Fürst.')
result = parser.svo_searcher(text)
print(result)