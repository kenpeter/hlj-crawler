from util import Util
from pymongo import MongoClient
from pprint import pprint

#utilObj = Util()
#utilObj.run()

client = MongoClient('mongodb://localhost:27017/hlj')
db = client.hlj
res = db.command("serverStatus")
pprint(res)