import mysql.connector

connection = mysql.connector.connect(user='moviebuff@moviebuff', password='CS411ssjb', host='moviebuff.mysql.database.azure.com', database='moviebuff')
cursor = connection.cursor()

title = raw_input("Title: ")
#title  = 'Speed'
query = ("SELECT imdb_title_id, year, genre from imdblist WHERE title='{}'").format(title)
print(query)
#title=input("Enter title: ")

cursor.execute(query)

for(imdb_title_id, year, genre) in cursor:
	print("{}, {}, {}").format(imdb_title_id, year, genre)
cursor.close()
connection.close()
