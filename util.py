from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
import urllib2
import os
import config

class Util:
  def __init__(self):
    self.client = MongoClient('mongodb://localhost:27017/hlj')
    self.db = self.client.hlj
    self.initLinkPart = 'https://hlj.com/search/go?p=Q&srid=S1-1DFWP&lbc=hobbylink&ts=custom&w=*&uid=699945098&method=and&af=selectmanufacturer%3abandai&isort=globalpop&view=grid&srt='
    self.productStartNum = 12*100

  def cleanQueueTable(self):
    db = self.db
    db.queue.drop()
    db.queueAt.drop()

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
    dirname = filename.split('_')[0]
    return dirname, filename

  def writeToDB(self, imgLink):
    # insert
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
    self.db.queue.insert_one(obj)

  def download_web_image(self, url, folder_base, folder_name, file_name):
    try:
      dir_path = folder_base + '/' + folder_name
      if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    except IOError as e:
        print('io error', e)
    except Exception as e:
        print('exception', e)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    request = urllib2.Request(url, headers=headers)
    img = urllib2.urlopen(request).read()
    with open (dir_path + '/' + file_name, 'w') as f: f.write(img)

  def buildQueueTable(self):
    # no clean up
    # self.cleanQueueTable()

    arr = self.getLinkArr()
    # headless
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome(executable_path=config.chromedriver, chrome_options=options)

    # listing page
    for linkItem in arr:

      # indicate
      print('-- linkItem --')
      print(linkItem)

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

          # write to db
          self.writeToDB(src) 

          # dl and write to file
          dirname, filename = self.parseImgLink(src)
          self.download_web_image(src, 'files', dirname, filename)
      
      # next link
      self.updateQueueAtHistory(linkItem)

    # quit
    browser.quit()


    print("done")