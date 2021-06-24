title_name = "SELECT * FROM imdblist WHERE title = %s"

title_year_name = 'SELECT imdb_title_id, year, genre from imdblist WHERE Title=%s AND year IN (%s..%s)'

delete_by_id = 'DELETE FROM imbdblist WHERE id=%s'

delete_review_by_id = 'DELETE FROM reviews WHERE id=%s'

def insert_record(form: dict) -> tuple:

    sqls = 'INSERT INTO imdblist ('
    attributes = []
    values = []
    ref_tag = []

    for k,v in form.items():
        if v:
            attributes.append(k)
            values.append(v)
            ref_tag.append('%s')

    sqls += ','.join(attributes) + ') VALUES ('
    sqls += ','.join(ref_tag) + ')'

    return (sqls,tuple(values))


def update_record(form: dict) -> tuple:

    sqls = 'UPDATE imdblist SET'
    title_id = form.pop('title_id')
    values = []
    for k,v in form.items():
        if v:
            sqls += ' %s = %s'
            values.append(k)
            values.append(v)

    sqls += ' WHERE title_id = %s'
    values.append(title_id)

    return (sqls,tuple(values))

def insert_review(form: dict) -> tuple:

    sqls = 'INSERT INTO reviews ('
    attributes = []
    values = []
    ref_tag = []

    for k,v in form.items():
        if v:
            attributes.append(k)
            values.append(v)
            ref_tag.append('%s')

    sqls += ','.join(attributes) + ') VALUES ('
    sqls += ','.join(ref_tag) + ')'

    return (sqls,tuple(values))


def update_review(form: dict) -> tuple:

    sqls = 'UPDATE reviews SET'
    review_id = form.pop('review_id')
    values = []
    for k,v in form.items():
        if v:
            sqls += ' %s = %s'
            values.append(k)
            values.append(v)

    sqls += ' WHERE review_id = %s'
    values.append(review_id)

    return (sqls,tuple(values))


def clean_filters(form: dict) -> dict:
    '''Process filter fields'''
    if(len(form['languages']) == 19):
        form['languages'] = None
    else:
        form['languages'] = [item for sublist in form['languages'] for item in sublist] #flatten list
    if(len(form['genres']) == 17):
        form['genres'] = None
    else:
        form['genres'] = [item for sublist in form['genres'] for item in sublist] #flatten list
    if(form['yearStart']=='1900' and form['yearEnd']=='2021'):
        form['yearStart'] = None
        form['yearEnd'] = None
    if (form['imdbStart']=='0' and form['imdbEnd']=='10'):
        form['imdbStart'] = None
        form['imdbEnd'] = None
    form.pop('rottenStart')

    return form

def query_enhanced(form:dict) -> list:
    '''Cleanup form and convert to stored proc signature as list'''
    form = clean_filters(form)
    languages = form['languages']
    services = form['streaming_services']
    genres = form['genres']
    year_start = form['yearStart']
    year_end = form['yearEnd']
    imdb_start = form['imdbStart']
    imdb_end = form['imdbEnd']
    sort_by = form['sorting']
    
    return [genres, languages, services, year_start, year_end, imdb_start, imdb_end, sort_by]
    

filter_search_rating = "select imdb_title_id, title, year, genre, language, avg_vote from imdblist where year >= %s and year <= %s and avg_vote >= %s and avg_vote <= %s order by avg_vote desc"

filter_search_date = "select imdb_title_id, title, year, genre, language, avg_vote from imdblist where year >= %s and year <= %s and avg_vote >= %s and avg_vote <= %s order by year desc"

filter_search_title = "select imdb_title_id,title, year, genre, language, avg_vote from imdblist where year >= %s and year <= %s and avg_vote >= %s and avg_vote <= %s order by title"

imdb_id = "SELECT * FROM imdblist WHERE imdb_title_id = %s"

imdb_id_reviews_createView = "CREATE OR REPLACE VIEW v1 as SELECT * FROM reviews NATURAL JOIN reviewtext JOIN imdblist ON reviews.TitleId = imdblist.imdb_title_id WHERE TitleId = %s"
imdb_id_reviews_readView = "SELECT * from vwtitledata WHERE TitleID = %s AND ReviewScore IS NOT NULL"

imdb_review_by_reviewId = "SELECT * FROM reviews JOIN reviewtext ON reviews.ReviewId = reviewtext.ReviewId WHERE reviews.ReviewId = %s"

remove_review_by_reviewId = "DELETE FROM reviews WHERE ReviewId = %s"
remove_reviewtext_by_reviewId = "DELETE FROM reviewtext WHERE ReviewId = %s"

create_review = "CALL createReview(%s, %s, %s, %s)"

update_review = "UPDATE reviews SET reviewscore = %s, UpdatedByUserID = %s, UpdatedByDate = CURRENT_TIMESTAMP WHERE ReviewID = %s"
update_reviewtext = "UPDATE reviewtext SET Review = %s WHERE ReviewID = %s"

add_user = "INSERT INTO user (UserName, EmailAddress, Password) values (%s, %s, %s)"

login = "SELECT COUNT(*) FROM user WHERE UserName = %s AND Password = %s"

getUserNameCount = "SELECT COUNT(*) FROM user where UserName = %s"

getUserID = "SELECT UserID from user where UserName = %s"

name = "SELECT imdb_title_id, category FROM imdbprincipals WHERE imdb_name = %s"

realName = "SELECT name FROM imdbnames WHERE imdb_name = %s"

nameData = "SELECT imdb_name, category FROM imdbprincipals WHERE imdb_title_id = %s order by category"

movieById = "SELECT title, year from imdblist where imdb_title_id = %s"

chatbot = "select imdb_title_id, title, genre, language from imdblist, streaming where imdblist.title = streaming.STitle"

streaming = "select imdb_title_id, title, year, genre, language, avg_vote, Netflix, Hulu, Prime, Disney from imdblist, streaming where imdblist.title = streaming.STitle and year >= %s and year <= %s and avg_vote >= %s and avg_vote <= %s"





