import requests
import os
from bs4 import BeautifulSoup


def get_web_text(url):
    webpage = requests.get(url)
    raw_text = BeautifulSoup(webpage.text, "html.parser")
    div = raw_text.find(id="gutenb").get_text()
    return div


def write_into_file(text):
    os.chdir("C:/Users/din_m/PycharmProjects/Masterarbeit/")
    with open("file.txt", "w") as file:
        file.writelines(text)


def main():
    url = "http://gutenberg.spiegel.de/buch/der-idiot-2098/"
    page = 1
    text = ""
    while page <= 50:
        text += get_web_text(url + str(page))
        print("Read page " + str(page) + " from 50.")
        page += 1

    write_into_file(text)

main()
#text = get_web_text("http://gutenberg.spiegel.de/buch/der-idiot-2098/1")
#print(text)
#print(text.encode('utf-8'))
#write_into_file()

