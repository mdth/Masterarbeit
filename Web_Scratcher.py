from bs4 import BeautifulSoup
import urllib

def get_web_text(url):
	webpage = urllib.urlopen('http://www.aflcio.org/Legislation-and-Politics/Legislative-Alerts').read()
	soup = BeautifulSoup(webpage)

	soup.find(id="gutenb")
get_web_text 