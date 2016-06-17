import requests
import os
from bs4 import BeautifulSoup


def get_web_text(url):
    webpage = requests.get(url)
    raw_text = BeautifulSoup(webpage.text, "html.parser")
    div = raw_text.find(id="gutenb").get_text()
    return div


def write_into_file(text, filename, file_path):
    os.chdir(file_path)
    with open("Chapter " + str(filename) + ".txt", "w") as file:
        file.writelines(text)


def main(save_path):
    url = "http://gutenberg.spiegel.de/buch/der-idiot-2098/"
    page = 1
    while page <= 50:
        text = get_web_text(url + str(page))
        write_into_file(text, page, save_path)
        print("Read page " + str(page) + " from 50.")
        page += 1

path = "C:/Users/din_m/PycharmProjects/Masterarbeit/Der Idiot"
main(path)