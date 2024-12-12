from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import datetime

sources = [
    'https://fpvua.org/forums/pitannja-ta-vidpovidi.22/',
    'https://fpvua.org/forums/remont-ta-obslugovuvannja.40/',
    'https://fpvua.org/forums/sholomi-ta-okuljari.16/',
    'https://fpvua.org/forums/kontrolleri.14/',
    'https://fpvua.org/forums/akumuljatori-ta-zarjadki.47/',
    'https://fpvua.org/forums/betaflight.28/'
]
next_page_css_selector = '#top > div.p-body > div > div.p-body-main > div.p-body-content > div > div > div:nth-child(1) > div > nav > div.pageNav > a'
user_tag = 'User'
assistant_tag = 'Assistant'


def get_threads(driver: webdriver, section_url: str) -> list[str]:
    driver.get(section_url)
    thread_elements = driver.find_elements(By.CLASS_NAME, 'structItem--thread')
    thread_links = []
    for t in thread_elements:
        link_elem = t.find_element(By.CLASS_NAME, "structItem-title").find_element(By.TAG_NAME, 'a')
        thread_links.append(link_elem.get_attribute('href'))

    return thread_links


def process_thread(driver, thread_url) -> pd.DataFrame:
    question_answer = {'Question': [], 'Answer': [], 'Source': []}

    driver.get(thread_url)
    article_elements = driver.find_elements(By.TAG_NAME, 'article')
    del article_elements[2-1::2] # Necessary. For some reason additional empty article is in every 2 item. 
    question = article_elements[0].find_element(By.CLASS_NAME, 'bbWrapper').text

    for i in range(1, len(article_elements)-1, 1):
        user = article_elements[i].find_element(By.CLASS_NAME, 'username').text # only direct response will have correct user
        content = article_elements[i].find_element(By.CLASS_NAME, 'bbWrapper').text

        if user == "": # skip nested responses
            continue
        question_answer['Question'].append(question)
        question_answer['Answer'].append(content)
        question_answer['Source'].append(thread_url)

    return pd.DataFrame(question_answer)


def main():
    driver = webdriver.Chrome()
    thread_links = []
    for url in sources:
        thread_links.extend(get_threads(driver, url))

    print(f'Processing {len(thread_links)} links...')

    frames = []

    for tl in thread_links:
        frames.append(process_thread(driver, tl))

    df = pd.concat(frames)

    filename = f"fpvua_{datetime.datetime.now()}"
    df.to_csv(filename, index=False)


if __name__ == '__main__':
    main()
