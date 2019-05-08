from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime

class Util:
  def __init__(self):
    self.client = MongoClient('mongodb://localhost:27017/hlj')
    self.db = self.client.hlj
    self.initLinkPart = 'https://hlj.com/search/go?p=Q&srid=S1-1DFWP&lbc=hobbylink&ts=custom&w=*&uid=699945098&method=and&af=selectmanufacturer%3abandai&isort=globalpop&view=grid&srt='
    self.productStartNum = 12

  def cleanQueueTable(self):
    db = self.db
    db.queue.drop()

  def isCollectionExisted(self, nameNeed):
    names = self.db.collection_names()
    for name in names:
      if(name == nameNeed):
        return True

    return False

  def updateQueueAtHistory(self, link):
    queueAt = self.db.queueAt
    myquery = {}
    newvalue = { "$set": { "history": link } }
    queueAt.update_one(myquery, newvalue)

  def getLinkArr(self):
    if(not self.isCollectionExisted('queueAt')):
      obj = {
        'history': self.initLinkPart + '0'
      }
      self.db.queueAt.insert_one(obj)

    item = self.db.queueAt.find_one()
    historyUrl = item['history']

    #
    arr=[]
    i = int(historyUrl[-1])
    len = self.productStartNum
    link = self.initLinkPart
    while i<=len:
      newlink = link + str(i)
      arr.append(newlink)
      i = i+12
    return arr

  def parseImgLink(self, imgLink):
    filename = imgLink.rsplit('/', 1)[-1]
    dirname = filename.rsplit('_', 1)[0]
    return dirname, filename

  def buildQueueTable(self):
    db = self.client.hlj

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

          # indicate
          print(src)

          imgSrcArr.append(src)    
      
      # next link
      self.updateQueueAtHistory(linkItem)

    # quit
    browser.quit()

    
    # insert
    for imgLink in imgSrcArr:
      dirname, filename = self.parseImgLink(imgLink)
      obj = {
        'imgLink': imgLink,
        'category': 'bandai',
        'dirname': dirname,
        'filename': filename,
        'updateDate': datetime.now(),
        'createdDate': datetime.now(),
        'status': ''
      }
      db.queue.insert_one(obj)

    print("done")