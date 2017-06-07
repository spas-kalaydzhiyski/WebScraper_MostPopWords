from bs4 import BeautifulSoup
from tabulate import tabulate
from stop_words import get_stop_words
import requests
import re
import operator
import json
import sys


# Get the data from Wikipedia
wikipedia_api_link = 'https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch='
wikipedia_link = 'https://en.wikipedia.org/wiki/'


# ---------------- HELPER METHODS ----------------------------


def cleanWord(word: str):
    return re.sub('[^A-Za-z]+', '', word)


def getWordList(url: str):
    word_list = []
    response = requests.get(url)
    response_text = response.text
    soup = BeautifulSoup(response_text, 'lxml')

    for paragraph in soup.findAll('p'):
        if paragraph.text is None:
            continue

        content = paragraph.text
        words = content.lower().split()

        for word in words:
            cleaned_word = cleanWord(word)
            if len(cleaned_word) > 0:
                word_list.append(cleaned_word)

    return word_list


def createFrequencyTable(word_list):
    word_count = {}

    for word in word_list:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    return word_count


def removeStopWords(frequency_list):
    stop_words = get_stop_words('en')
    result_list = []

    for key, value in frequency_list:
        if key not in stop_words:
            result_list.append([key, value])

    return result_list

# --------------------- HELPER METHODS (END) -------------------------------------


def main():
    if len(sys.argv) < 2:
        print('Enter a valid input.')
        exit()

    # Get the search word from the program parameters
    string_query = sys.argv[1]
    if len(sys.argv) > 2:
        search_mode = True
    else:
        search_mode = False

    # Create the URL
    url = wikipedia_api_link + string_query

    try:
        response = requests.get(url)
        data = json.loads(response.content.decode('utf-8'))

        # Format the response data
        wikipedia_page_tag = data['query']['search'][0]['title']

        # Create the new URL
        url = wikipedia_link + wikipedia_page_tag
        page_word_list = getWordList(url)

        # Create table of word counts
        page_word_count = createFrequencyTable(page_word_list)
        items = page_word_count.items()
        sorted_word_frequency_list = sorted(items, key=operator.itemgetter(1), reverse=True)

        if search_mode:
            sorted_word_frequency_list = removeStopWords(sorted_word_frequency_list)

        # Sum the total words to get the frequencies
        total_words_sum = 0
        for key, value in sorted_word_frequency_list:
            total_words_sum += value

        # Get the top 20 words
        if len(sorted_word_frequency_list) > 20:
            sorted_word_frequency_list = sorted_word_frequency_list[:20]

        final_list = []
        for key, value in sorted_word_frequency_list:
            percentage_value = float(value * 100 / total_words_sum)
            final_list.append([key, value, round(percentage_value, 4)])

        print_headers = ['Word', 'Frequency', 'Frequency Percentage']

        # Print the table with tabulate
        print(tabulate(final_list, headers=print_headers, tablefmt='orgtbl'))

    except requests.exceptions.Timeout as e:
        print(e.response + "\nThe server did not respond.")

if __name__ == '__main__':
    main()
