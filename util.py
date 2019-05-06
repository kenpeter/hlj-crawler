from bs4 import BeautifulSoup
from selenium import webdriver

class Util:
  def __init__(self):
    pass

  def getLinkArr(self):
    arr=[]
    i=0
    len = 0
    link = 'https://hlj.com/search/go?p=Q&srid=S1-1DFWP&lbc=hobbylink&ts=custom&w=*&uid=699945098&method=and&af=selectmanufacturer%3abandai&isort=globalpop&view=grid&srt='
    while i<=len:
      newlink = link + str(i)
      arr.append(newlink)
      i = i+12
    return arr

  def buildQueueTable(self):
    imgSrcArr = []
    arr = self.getLinkArr()
    # headless
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)

    # listing page
    for linkItem in arr:
      browser.get(linkItem)
      pageSource = browser.page_source
      groupHtml = BeautifulSoup(pageSource, 'lxml')
      productLinks = groupHtml.find_all("a", "product-item-photo")

      # build product links
      productData = {}
      for link in productLinks:
        val = link.attrs['href']
        productData[val] = val

      for link in productData:
        browser.get(link)
        pageSource = browser.page_source
        productHtml = BeautifulSoup(pageSource, 'lxml')
        productImgs = productHtml.find_all('img', 'fotorama__img')

        for img in productImgs:
          # https://hlj.com/media/catalog/product/cache/image/e9c3970ab036de70892d86c6d221abfe/b/a/bans57842_3.jpg          
          src = img['src']

          if src.find("80x60") != -1:
            continue

          imgSrcArr.append(src)    
  
    print(imgSrcArr)

    browser.quit()