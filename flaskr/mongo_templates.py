""" Mongo_templates: Query templates for various filtering and ordering operations"""

LANG_BITMAP = {'Arabic': 1, 'Cantonese': 2, 'Danish': 4, 'English': 8, 'French': 16, 'German': 32, 'Hebrew': 64\
    , 'Hindi': 128, 'Italian': 256, 'Japanese': 512, 'Korean': 1024, 'Latin': 2048, 'Mandarin': 4096, 'Other': 8192\
        , 'Portugese': 16384, 'Russian': 32768, 'Spanish': 65536, 'Swedish': 131072, 'Ukrainian': 262144}
GENRE_BITMAP = {'Action': 1, 'Adventure': 2, 'Animation': 4, 'Biography': 8, 'Comedy': 16, 'Crime': 32, 'Drama': 64\
    , 'Fantasy': 128, 'History': 256, 'Horror': 512, 'Musical': 1024, 'Mystery': 2048, 'Romance': 4096, 'Sci-Fi': 8192\
        , 'Thriller': 16384, 'War': 32768, 'Western': 65536}
STREAM_BITMAP = {'Disney': 1, 'Hulu': 2, 'Netflix': 4, 'Prime': 8}


def clean_filters(form: dict) -> dict:
    '''Process filter fields'''
    if form['languages']:
        form['languages'] = [item for sublist in form['languages'] for item in sublist] #flatten list
    if form['genres']:
        form['genres'] = [item for sublist in form['genres'] for item in sublist] #flatten list
    if 'streaming' in form:
        form['streaming'] = [item for sublist in form['streaming'] for item in sublist] #flatten list
        if len(form["streaming"]) < 1:
            form.pop("streaming")
        else:
            if "Disney" in form["streaming"]:
                form["streaming"].append("Disney+")
    if len(form['languages']) == 19 or len(form['languages']) == 0:
        form.pop('languages')
    if len(form['genres']) == 17 or len(form['genres']) == 0:
        form.pop('genres')
    if form['yearStart']=='1900' and form['yearEnd']=='2021':
        form.pop('yearStart')
        form.pop('yearEnd')
    if 'imdbStart' in form and 'imdbEnd' in form:
        if (form['imdbStart']=='0' and form['imdbEnd']=='10'):
            form.pop('imdbStart')
            form.pop('imdbEnd')

    return form

def bitmap_filter_query(form: dict) -> dict:
    """ Returns aggregate query if bitmap filtering required """
    query = {}
    if "languages" in form:
        if "not_english" in form:   #chatbot custom bitmask operation
            if form["not_english"]:
                query.update({"bin_language": {"$bitsAllClear": 8}})
            else:
                mask = 0
                for x in LANG_BITMAP:
                    mask = mask | LANG_BITMAP[x]
                query.update({"$and": [
                                {"bin_language": {"$bitsAllSet": 8}},
                                {"bin_language": {"$bitsAllClear": mask-8}}
                            ]})
        else:
            langs = [x.strip() for x in form['languages']]
            mask = 0
            for x in langs:
                if x in LANG_BITMAP:
                    mask = mask | LANG_BITMAP[x]
            print("lang mask", mask)     
            query.update({"bin_language": {"$bitsAllSet": mask}})
    if "genres" in form:
        gens = [x.strip() for x in form['genres']]
        mask = 0
        for x in gens:
            if x in GENRE_BITMAP:
                mask = mask | GENRE_BITMAP[x]  
        print("genres mask", mask)   
        query.update({"bin_genre": {"$bitsAnySet": mask}})
    if "streaming" in form:
        streams = [x.strip() for x in form['streaming']]
        mask = 0
        for x in streams:
            if x in STREAM_BITMAP:
                mask = mask | STREAM_BITMAP[x]  
        print("streams mask", mask)   
        query.update({"bin_stream": {"$bitsAnySet": mask}})
    if query:
        if "yearStart" in form:
            q = year_range(form)
            query.update(q)   
        if "imdbStart" in form:
            q = rating_range(form)
            query.update(q)
        order = order_by(form)["$orderby"]
        return {"$query": query, "$orderby": order}
    else:
        return {}


def filter_query(form: dict) -> dict:
    """Clean filters and select correct query string"""
    query = {}
    filters = ["languages", "genres" , "streaming"]
    for f in filters:
        if f in form.keys():
            q = lang_genre_stream(form)
            query.update(q)
            break
    if "yearStart" in form:
        q = year_range(form)
        query.update(q)   
    if "imdbStart" in form:
        q = rating_range(form)
        query.update(q)
    order = order_by(form)["$orderby"]
    return {"$query": query, "$orderby": order}


def order_by(form: dict) -> dict:
    query = {}
    ordering = form['sorting']
    if ordering == "avg_vote":
        q = {"$orderby": { "avg_vote" : -1 }}
        query.update(q)
    elif ordering == "title":
        q = {"$orderby": { "title" : 1 }}
        query.update(q)
    else:   
        q = {"$orderby": { "year" : -1 }}
        query.update(q)
    return query


def lang_genre_stream(form: dict) -> dict:
    print("lang_genre_stream")
    query = {}
    if "languages" in form.keys():
        languages = form["languages"]
        q = { "language": { "$in": languages}}
        query.update(q)
    if "genres" in form.keys():
        genres = form["genres"]
        q = { "genre": { "$in": genres }}
        query.update(q)
    if "streaming" in form.keys():
       services = form["streaming"]
       q = { "Streaming": { "$in": services }}
       query.update(q)
    return query


def year_range(form: dict) -> dict:
    start = form['yearStart']
    end = form['yearEnd']
    return { "year" : { "$gte" :  start, "$lte" : end}}


def rating_range(form: dict) -> dict:
    start = form['imdbStart']
    end = form['imdbEnd']
    if end == "10":
        end = "9.99"
    return { "avg_vote" : { "$gte" :  start, "$lte" : end}}

def query_titles_by_person(name: str) -> dict:
    return {"Principals.name.name": name}

def query_titles_by_person_many(names: list) -> dict:
    return {"Principals.name.name": { "$in": names}}

def full_text_search_name(searchterm):   
    return [{"$search": {
                "index": "default", # optional, defaults to "default"
                "autocomplete": {
                    "query": searchterm,
                    "path": "Name",
                    "tokenOrder": "sequential",
                    #"fuzzy": <options>,
                    #"score": <options>
                    }
                }
            },
            {"$limit": 15 },
            {"$project": {  
                "_id": 0,
                "Name": 1,
                "category": 1
                }
            }]

def full_text_search_title(searchterm):   
    return [{"$search": {
                "index": "default", # optional, defaults to "default"
                "autocomplete": {
                    "query": searchterm,
                    "path": "title",
                    "tokenOrder": "sequential",
                    #"fuzzy": <options>,
                    #"score": <options>
                    }
                }
            },
            {"$limit": 15 },
            {"$project": {  
                "_id": 0,
                "title": 1
                }
            }]

def full_text_search_description(searchterm):   
    return [{"$search": {
                "index": "default", # optional, defaults to "default"
                "autocomplete": {
                    "query": searchterm,
                    "path": "title",
                    "tokenOrder": "sequential",
                    #"fuzzy": <options>,
                    #"score": <options>
                    }
                }
            },
            {"$limit": 15 },
            {"$project": {  
                "_id": 0,
                "title": 1,     # mislabeled, this is actually description field
                "Imdb_Title_id": 1
                }
            }]

