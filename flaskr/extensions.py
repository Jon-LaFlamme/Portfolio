#Connection persistence strategy adapted from @vincent31337, Stack Overflow: 
#https://stackoverflow.com/questions/55523299/best-practices-for-persistent-database-connections-in-python-when-using-flask

from flaskr.db import MoviebuffDB
from flaskr.cosmos import MoviebuffCosmos
from flaskr.mongo import MongoDB

db = MoviebuffDB()
cosmos_db = MoviebuffCosmos()
mongo_db = MongoDB()



