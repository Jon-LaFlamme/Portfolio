import pymysql
from flaskr import sqls as sqls
import hashlib, uuid
import sys

class MoviebuffDB():
    def __init__(self):
        self.app = None
        self.driver = None
    
    def init_app(self, app):
        self.app = app

    def close_connection(self):
        self.driver.close()
        self.driver = None

    def connect(self):
        self.driver = pymysql.connect(user='moviebuff@moviebuff',\
                                password='CS411ssjb',\
                                host='moviebuff.mysql.database.azure.com',\
                                ssl_disabled=True,\
                                database='moviebuff',\
                                charset='utf8mb4',\
                                autocommit=True,\
                                cursorclass=pymysql.cursors.DictCursor)

    def query_basic(self, query: str) -> dict:
        self.connect()
        sql = sqls.title_name
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchone()
        self.close_connection()
        return res

    def query_id(self, query: str):
        if not self.driver:
            self.connect()
        sql = sqls.imdb_id
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchone()
        self.close_connection()
        return res

    def query_nmData(self, query: str):
        if not self.driver:
            self.connect()
        sql = sqls.nameData
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def query_movieName(self, query: str):
        '''Quick Search: Target for Demo on Mar 14'''
        if not self.driver:
            self.connect()
        sql = sqls.movieById
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchone()
        self.close_connection()
        return res

    def query_nm(self, query: str):
        '''Quick Search: Target for Demo on Mar 14'''
        if not self.driver:
            self.connect()
        sql = sqls.name
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def query_rName(self, query: str):
        '''Quick Search: Target for Demo on Mar 14'''
        if not self.driver:
            self.connect()
        sql = sqls.realName
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()    
        return res

    def filter_chatbot(self, param):
        self.connect()
        sql = sqls.chatbot
        sql += " and (" + param + " = 1) order by avg_vote desc limit 500"
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql)
            res = c.fetchall()
        self.close_connection()
        return res

    def filter_streaming(self, query: str, Services):
        self.connect()
        sql = sqls.streaming
        sql += " and ("
        for i in Services[:-1]:
            sql += i + " = 1 or "
        sql += Services[-1] + " = 1"
        sql += ") order by avg_vote desc"
        res = {"Query result": 0}
        print(sql, file=sys.stderr)
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def filter_streaming_date(self, query: str, Services):
        self.connect()
        sql = sqls.streaming
        sql += " and ("
        for i in Services[:-1]:
            sql += i + " = 1 or "
        sql += Services[-1] + " = 1"
        sql += ") order by year desc"
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def filter_streaming_title(self, query: str, Services):
        self.connect()
        sql = sqls.streaming
        sql += " and ("
        for i in Services[:-1]:
            sql += i + " = 1 or "
        sql += Services[-1] + " = 1"
        sql += ") order by title"
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def filter_query(self, query: str):
        self.connect()
        sql = sqls.filter_search_rating
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def filter_query_date(self, query: str):
        self.connect()
        sql = sqls.filter_search_date
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def filter_query_title(self, query: str):
        self.connect()
        sql = sqls.filter_search_title
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def query_enhanced(self, form: dict) -> dict:
        """Processes filters and calls stored proc: GetMoviesByCriteria() """
        self.connect()
        res = {"Not yet implemented": 0}
        with self.driver.cursor() as c:
            proc_args = sqls.query_enhanced(form)
            c.execute("call GetMoviesByCriteria(?, ?, ?, ?, ?, ?, ?, ?)", proc_args)
            res = c.fetchall()  
        self.close_connection()         
        return res

    def login(self, userInfo):
        if not self.driver:
            self.connect()
        sql = sqls.login
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, (userInfo[0], hashlib.md5(userInfo[1].encode()).hexdigest()))
            res = c.fetchone()
        self.close_connection()
        if(res['COUNT(*)'] >= 1):
            return True
        else:
            return False

    def getUserID(self, query: str):
        if not self.driver:
            self.connect()
        sql = sqls.getUserID
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchone()
        self.close_connection()
        return res['UserID']

    def addUser(self, userInfo):
        if not self.driver:
            self.connect()
        sql = sqls.add_user
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            try:
                c.execute(sqls.getUserNameCount, userInfo[0])
                res = c.fetchone()
                if (res['COUNT(*)'] >= 1):
                    self.close_connection()
                    return False
                c.execute(sql, (userInfo[0], userInfo[1], hashlib.md5(userInfo[2].encode()).hexdigest()))
                self.driver.commit()
            except:
                self.close_connection()
                return False
        self.close_connection()
        return True

    def query_id_reviews(self, query: str):
        if not self.driver:
            self.connect()
        #sql = sqls.imdb_id_reviews_createView
        sql2 = sqls.imdb_id_reviews_readView
        res = {"Query result": 0}
        with self.driver.cursor() as c:
        #    c.execute(sql, query)
            c.execute(sql2, query)
            res = c.fetchall()
        self.close_connection()
        return res
 
    def query_review_by_reviewid(self, query: str):
        if not self.driver:
            self.connect()
        sql = sqls.imdb_review_by_reviewId
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def remove_review_by_reviewid(self, query: str):
        if not self.driver:
            self.connect()
        sql = sqls.remove_review_by_reviewId
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def remove_reviewtext_by_reviewid(self, query: str):
        if not self.driver:
            self.connect()
        sql = sqls.remove_reviewtext_by_reviewId
        res = {"Query result": 0}
        with self.driver.cursor() as c:
            c.execute(sql, query)
            res = c.fetchall()
        self.close_connection()
        return res

    def delete_review(self, s: str) -> dict:
        self.connect()
        k = -1
        with self.driver.cursor() as c:
            sql = sqls.delete_review_by_id(s)
            num = c.execute(sql, s) 
        self.close_connection()       
        return {"Number of reviews deleted from database": k}

    def create_review(self, UserID, Score, TitleID, Review) -> dict:
        self.connect()
        with self.driver.cursor() as c:
            sql = sqls.create_review
            num = c.execute(sql, (TitleID, UserID, Review, Score))
        self.driver.commit()
        self.close_connection()
        return {"Created": True}

    def update_review(self, Score, UserID, ReviewID, Review) -> dict:
        self.connect()
        with self.driver.cursor() as c:
            sql = sqls.update_review
            num = c.execute(sql, (Score, UserID, ReviewID)) 
            sql = sqls.update_reviewtext
            num = c.execute(sql, (Review, ReviewID)) 
        self.close_connection()       
        return {"Updated": True}
