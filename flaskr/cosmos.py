from azure.cosmos import CosmosClient
from flaskr import sqls as sqls
import json

#Note: API targets REST api-version=2019-05-06

class MoviebuffCosmos():
    def __init__(self):
        self.app = None
        self.client = None
        self.db = None
        self.container = None
    
    def init_app(self, app):
        self.app = app

    def close_connection(self):
        self.client = None
        self.db = None
        self.container = None

    def connect(self):
        URL = "https://moviebuffnosql.documents.azure.com:443/"
        KEY = "VvLbsj2ASoYhdstlhBR8DLV0U0mwb1hShUCkEpltp3dBKmbn9XXZVLoxSFi0qU6QgebqH7TujrNIu23C7ZufPw=="
        DB_Name = "Moviebuff"
        CONTAINER_NAME = 'results'
        self.client = CosmosClient(URL, KEY)
        self.db = self.client.get_database_client(DB_Name)
        self.container = self.db.get_container_client('title')

                                                       
    def query_enhanced(self, _id: str) -> list:
        self.connect()
        #  5a931121-e77e-42a3-9b83-201ec0d15854     #Sample ID for NoSQL DB
        res = {"Not yet implemented": 0}
        query = "SELECT * FROM c WHERE c.imdb_title_id=@id"
        values = [{"name":'@id', "value": _id}]
        items = list(self.container.query_items(query=query, parameters=values,
                                          enable_cross_partition_query=True))
        self.close_connection()         
        return items
