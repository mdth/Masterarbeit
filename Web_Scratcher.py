import requests
import os
from bs4 import BeautifulSoup


def get_web_text(url):
    webpage = requests.get(url)
    raw_text = BeautifulSoup(webpage.text, "html.parser")
    print(raw_text.prettify())
    #div = raw_text.find(id="gutenb").get_text()
    div = raw_text.find_all("div", class_="jnnorm")
    text = ''
    for item in div:
        item.get_text()
        text = text + item.get_text()
    return text


def write_into_file(text, filename, file_path):
    os.chdir(file_path)
    with open("GG Teil " + str(filename) + ".txt", "w", encoding='utf-8') as file:
        file.writelines(text)


def main(save_path):
    #url = "http://gutenberg.spiegel.de/buch/der-idiot-2098/"
    url = "https://www.gesetze-im-internet.de/gg/BJNR000010949.html"
    #url = "https://www.bundestag.de/parlament/aufgaben/rechtsgrundlagen/grundgesetz/gg_01"
    #url_2 = "/245122"
    page = 1
    text = get_web_text(url)
    write_into_file(text, page, save_path)
    print("Read page " + str(page) + " from 14.")

main(os.getcwd())