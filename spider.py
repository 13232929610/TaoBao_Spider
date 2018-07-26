from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from urllib.parse import quote


keywords = 'iPhone'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(driver, 10)
base_url = 'https://s.taobao.com/search?q='
url = base_url + quote(keywords)
driver.get(url)


def index_page(page):
    print('正在请求第', page, '页')
    try:
        input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#mainsrp-pager div.form > input')))
        input.clear()
        input.send_keys(page)
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#mainsrp-pager div.form > span.btn.J_Submit')))
        submit.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
        print('已到达', page, '页')
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.m-itemlist')))
        print('正在抓取···')
        get_products(driver.page_source)
    except TimeoutException:
        print('请求第', page, '超时')
        print('正在重试···')
        index_page(page)


def get_products(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('#mainsrp-itemlist .items .item')
    try:
        for item in items:
            dict = {
                '名称': item.select_one('.pic .J_ItemPic').attrs['alt'],
                '链接': 'https:' + item.select_one('.J_ClickStat').attrs['data-href'],
                '图片': 'https:' + item.select_one('.pic-link .img').attrs['data-src'],
                '价格': item.select_one('.price').get_text().strip(),
                '店铺': item.select_one('.shop').get_text().strip(),
                '地区': item.select_one('.location').get_text(),
                '付款人数': item.select_one('.deal-cnt').get_text()[:-3]
               }
            print(dict)
    except Exception:
        print('爬取异常')


if __name__ == '__main__':
    for page in range(1, 21):
        index_page(page)
    driver.close()
