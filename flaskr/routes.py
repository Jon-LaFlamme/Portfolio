from flask import Flask, request, redirect, render_template, g, url_for, session, jsonify
import wtforms_jsonschema2
from json2html import *
from flaskr.forms import Title
from flaskr.db import MoviebuffDB
from flaskr.cosmos import MoviebuffCosmos
from flaskr.mongo import MongoDB
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
from flaskr import app
import requests
import json
from flaskr import sqls as sqls
import random

db = MoviebuffDB()
cosmos_db = MoviebuffCosmos()
mongo_db = MongoDB()

convoList = []
category = "search term"
prompt = ""
back = []
filterDict = {}

ServicesList = ['Netflix', 'Prime', 'Hulu', 'Disney']
earliestYear = 1900
lowestRating = 0
languageList = ['English','Spanish','German','Italian','French','Russian','Danish','Swedish','Japanese','Hindi','Mandarin','Arabic','Korean','Portugese']
genreList = ['Action','Adventure','Animation','Biography','Comedy','Crime',
             'Drama','Fantasy','History','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western']


ANY = ["any", 'all', 'all of the above', 'all of them', 'every', 'every one']
NO = ['no', 'nope', 'no thanks', 'negative', 'n', 'sorry']
YES = ['yes', 'sure', 'okay', 'alright', 'y', 'yup', 'ya', 'yeah','maybe', 'definitely', 'ok', 'k', 'possibly', 'certainly']
BACK = ['back', 'b', 'go back', 'backwards', 'last']
AMBIGUOUS = ["any", "either", 'neither', 'none', 'all', "none", "no preference", "doesn't matter", "don't care"]
CAST_CREW = ['cast/crew', 'cast/crew member', 'cast', 'crew', 'member', 'actor', 'director', 'writer',\
         'producer', 'actress', 'cinematographer', 'person', 'human', 'people', 'role']
MOVIE_NAME = ['title', 'movie', 'moviename', 'title name', 'movie name', 'show']
KEYWORD = ['keyword', 'word', 'description', 'topic', 'topical', 'key']
OLDER = ["older", "old", "classic", "before", "before 1970", "something older",\
     "something older (before 1970)", "something older before 1970"]
NEWER = ["new", "release", "new-release", "newer", "recent", "releases"]
BETWEEN = ["in-between", "between", "in between"]
SEARCHING = ["directly", "searching", "search", "query", "find", "direct", "specific", "find something"]
FILTERING = ["guide", "guide me", "questions", "help", "help me"]


ERROR = "I'm sorry, I don't understand. "
GREETING = "Hi! I'm Candice. Can I help you find a movie today?"
EXIT_STRING = "Sorry, I can't help you today. Please navigate to the home page to search titles yourself.\
             If you change your mind, I will be here to help!"
CHECK_QUERY_TYPE = "Would you like to find something specific or let me guide you with some questions?"
DIRECT_QUERY_CATEGORY = "Perfect, would you like to search by title, cast/crew member or keyword?"
DIRECT_QUERY_TERM_PREFIX = "Alright. What is the "
DIRECT_QUERY_TERM_SUFFIX = " you'd like me to search for?"
RESULTS = "Searching now.. Results should display momentarily."
NO_RESULTS = "Sorry, I couldn't find any results matching your query. Please try another term."

FILTER_GENRE_PREFIX = "No problem. We can narrow down your choices, starting with genre."
FILTER_GENRE_SUFFIX = "Which genres are you interested in? I'll list some choices for you...\
            <br></br>" + "<br></br>".join(genreList)
FILTER_LANGUAGE = "Are you intersted in foreign or domestic films?"
FILTER_YEAR = "Are you looking for a new release, something older (before 1970), or something in-between?"
FILTER_STREAMING = "Would you also like to limit results to movies you can stream?"
FILTER_STREAMING_CHOICE = "Which streaming services? Netflix, Hulu, Disney or Prime?"

FAILURE = [{'imdb_title_id':"",
        'title':"Sorry, No Titles Found",
        'year':"N/A",
        'genre':"N/A",
        'language':"N/A",
        'avg_vote':'N/A',
        'Netflix':"N/A",
        'Hulu':"N/A",
        'Prime':"N/A",
        'Disney':"N/A"}]


bot = ChatBot("Candice")

trainer = ChatterBotCorpusTrainer(bot)
trainer.train("chatterbot.corpus.english")

# Train based on english greetings corpus
trainer.train("chatterbot.corpus.english.greetings")

# Train based on the english conversations corpus
trainer.train("chatterbot.corpus.english.conversations")

listTrainer = ListTrainer(bot)



for i in ServicesList:
    listTrainer.train([
        i,
        "Ok, we'll search for movies on the " + i + " streaming service. Please enter one of the following languages to search for : " + ' '.join(languageList)
    ])

for i in languageList:
    listTrainer.train([
        i,
        "Ok, we'll search for movies in the " + i + " language. Please enter one of the following genres to search for : " + ' '.join(genreList)
    ])

for i in genreList:
    listTrainer.train([
        i,
        "Ok, we'll search for movies in the " + i + " genre. Searching..."
    ])

#@app.route('/', methods=['GET','POST'])  #Basic Title Search/Home Page
@app.route('/')
def home():
    # if request.method == 'GET':
    #     return render_template('base.html')
    # else:
    #     query = request.form.get('Title')
    #     res = db.query_basic(query)
    #     return json2html.convert(json=res)
    return redirect("search")

@app.route('/__Candice', methods=['GET','POST'])  #Basic Title Search/Home Page
def Candice():
    mongo_db.query_by_person({'Name': "Brent Spiner"})  #dummy query to warmup connection
    global category
    global filterDict
    global prompt
    global back     # LIFO/Stack for backup feature
    category = None
    filterDict = {'imdbStart': '0', 'imdbEnd': '10', 'sorting': 'avg_vote', 'streaming': []}
    prompt = GREETING
    back.append(GREETING) 
    if request.method == 'GET':
        return render_template('candice.html')



@app.route('/getChat')
def getChat():
    userText = request.args.get('msg')
    words = userText.lower().split(" ")
    global category
    global filterDict
    global prompt
    global back
    if not back or prompt != back[-1]:
        back.append(prompt)
    
    if prompt == EXIT_STRING:  #Restart chatbot convo on any input
        prompt = GREETING
        return 'Hello again! May I help you find a movie?' 

    elif " ".join(words).strip() in BACK:     #Goes backwards in the chat dialogue
        if len(back) >= 2:
            back.pop()
            prompt = back.pop()
            if prompt in FILTER_GENRE_SUFFIX:
                if  'genes' in filterDict:
                    filterDict['genres'] = None
            if prompt in FILTER_LANGUAGE:
                if  'languages' in filterDict:
                    filterDict['languages'] = None
                    filterDict['streaming'] = []
            if prompt in FILTER_STREAMING:
                filterDict['streaming'] = []     
        return prompt

    elif prompt == GREETING:      #Hello, would you like help?     
        for word in words:
            if word in YES:
                prompt = CHECK_QUERY_TYPE  
                return CHECK_QUERY_TYPE
            elif word in NO:
                prompt = EXIT_STRING
                return EXIT_STRING
        else:     
            return ERROR + GREETING
     
    elif prompt == CHECK_QUERY_TYPE:    #Branch to filtering approach OR full text approach
        for word in words:
            if word in SEARCHING: # continue with full text search
                prompt = DIRECT_QUERY_CATEGORY
                return DIRECT_QUERY_CATEGORY 
            elif word in FILTERING:    # switch to filtering approach
                prompt = FILTER_GENRE_SUFFIX
                return FILTER_GENRE_PREFIX + FILTER_GENRE_SUFFIX
        else:
            return ERROR + CHECK_QUERY_TYPE
            
    elif prompt == DIRECT_QUERY_CATEGORY:      #Prompt for direct query term
        for word in words:
            if word in CAST_CREW:
                category = 'cast/crew'
                prompt = DIRECT_QUERY_TERM_PREFIX
                return DIRECT_QUERY_TERM_PREFIX + "person" + DIRECT_QUERY_TERM_SUFFIX
            elif word in MOVIE_NAME:
                category = 'title'
                prompt = DIRECT_QUERY_TERM_PREFIX
                return DIRECT_QUERY_TERM_PREFIX + "title" + DIRECT_QUERY_TERM_SUFFIX
            elif word in KEYWORD:
                category = 'description'
                prompt = DIRECT_QUERY_TERM_PREFIX
                return DIRECT_QUERY_TERM_PREFIX + "keyword" + DIRECT_QUERY_TERM_SUFFIX
        else:
            return ERROR + DIRECT_QUERY_CATEGORY
    
    elif DIRECT_QUERY_TERM_PREFIX == prompt:        #direct query on selected category
        res = None
        query = " ".join(words)
        if category == "cast/crew":
            cursor = mongo_db.full_text_search_name(query)
            if cursor:
                res = []
                for x in cursor:
                    res.append({"Name": x['Name'], "category": x['category']})
                return render_template('chatbot-search-person.html', results = res)
            else:
                return render_template('results-mongo.html', results = FAILURE)

        elif category == "description":
            cursor = mongo_db.full_text_search_description(query)
            if cursor:
                res = []
                ids = []
                titles = {}
                for x in cursor:
                    ids.append(x["Imdb_Title_id"])
                    res.append({"Imdb_Title_id": x["Imdb_Title_id"], "description": x["title"]})
                cursor = mongo_db.query_by_title_id_many(ids)
                if cursor:     
                    for x in cursor:
                        titles.update({x["Imdb_Title_id"]: x['title']})
                    for x in res:
                        _id = x["Imdb_Title_id"]
                        if _id in titles:
                            x.update({'title': titles[_id]})
                        else:
                            res.remove(x)        
                return render_template('chatbot-search-keyword.html', results = res)
            else:
                return render_template('results-mongo.html', results = FAILURE)

        else:   # title search
            cursor = mongo_db.full_text_search_title(query)
            if cursor:
                unique_res = set()
                for x in cursor:
                    unique_res.add(x['title'])
                titles = list(unique_res)
                res = mongo_db.query_by_title_name_many(titles)
        if not res:
            return NO_RESULTS
        else:         
            results = []
            for title in res:
                results.append(title)
            return render_template('results-mongo.html', results = results)

    elif FILTER_GENRE_SUFFIX in prompt:     #Determine genre preferences
        valid_genres = []
        for word in words:      
            if word in AMBIGUOUS:           
                valid_genres = genreList 
        if not valid_genres: 
            for word in words:
                word = word.replace(',', "").title().strip()
                if word in genreList:
                    valid_genres.append(word)
        if valid_genres:
            filterDict['genres'] = valid_genres
            prompt = FILTER_LANGUAGE
            return FILTER_LANGUAGE
        else:
            return ERROR + FILTER_GENRE_SUFFIX
    
    elif prompt in FILTER_LANGUAGE:     #Determine foreign or domestic
        valid_languages = []
        for word in words:
            if word in AMBIGUOUS:           
                valid_languages = languageList 
        if not valid_languages:
            for word in words:
                word = word.replace(',', "").title().strip()
                if word in ['English', 'Domestic', 'U.S.', 'Local', "United States", "English-language"]:
                    valid_languages = ['English']
                    filterDict["not_english"] = False
                elif word in ["International", "Foreign", "Foreign-language"]:
                    valid_languages = languageList
                    filterDict["not_english"] = True
                    valid_languages.pop(0)  #pops English
                else:
                    return ERROR + FILTER_LANGUAGE
        if valid_languages:
            filterDict['languages'] = valid_languages
            prompt = FILTER_YEAR
            return FILTER_YEAR
        else:
            return ERROR + FILTER_LANGUAGE
                
    elif FILTER_YEAR == prompt:
        start = '1900'
        end = '2021'
        for word in words:
            word = word.replace(',', "").strip()
            print(word, file=sys.stderr) 
            if word in NEWER:
                start = '2019'
            elif word in OLDER:
                start = '1900'
                end = '1969'
            elif word in BETWEEN:
                start = '1970'
                end = '2018'
            else:
                return ERROR + FILTER_YEAR
        filterDict['yearStart'] = start 
        filterDict['yearEnd'] = end      
        prompt = FILTER_STREAMING
        return FILTER_STREAMING
    
    elif FILTER_STREAMING == prompt:
        for word in words:
            if word in YES:
                prompt = FILTER_STREAMING_CHOICE
                return FILTER_STREAMING_CHOICE
            elif word not in NO:
                return ERROR + FILTER_STREAMING
        filterDict['genres'] = [[x] for x in filterDict['genres']]
        filterDict['languages'] = [[x] for x in filterDict['languages']]
        if 'streaming' in filterDict:
            filterDict['streaming'] = [[x] for x in filterDict['streaming']]
        print("chatbot query: ", filterDict, file=sys.stderr)
        cursor = mongo_db.filter_query(filterDict)
        res = [mov for mov in cursor]
        if not res:
            res = FAILURE
        return render_template('results-mongo.html', results = res)

    elif prompt in FILTER_STREAMING_CHOICE:
        print("streaming choices: ", words, file=sys.stderr)
        if " ".join(words) in ANY:
            filterDict['streaming'] = ServicesList
        else:
            services = []
            for word in words:
                word = word.title().replace(",","").title().strip()     
                if word in ServicesList:
                    services.append(word)
                    filterDict['streaming'] = services
                else:
                    return ERROR + FILTER_STREAMING_CHOICE
        filterDict['genres'] = [[x] for x in filterDict['genres']]
        filterDict['languages'] = [[x] for x in filterDict['languages']]
        filterDict['streaming'] = [[x] for x in filterDict['streaming']]
        print("chatbot query: ", filterDict, file=sys.stderr)
        cursor = mongo_db.filter_query(filterDict)
        res = [mov for mov in cursor]
        if not res:
            res = FAILURE
        print(filterDict, file=sys.stderr)
        return render_template('results-mongo.html', results = res)
    
    else:   #Resets chatbot convo
        return GREETING
    
@app.route('/dummyquery')
def dummyquery():
    print("warming up MongoDB for subsequent pulls..", file=sys.stderr)
    mongo_db.query_by_person({'Name': "Brent Spiner"})
    return ""
    

@app.route('/Login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', failedLogin = False)
    if request.method == 'POST':
        if db.login([request.form.get('User'),request.form.get('Password')]):
            session['login'] = True
            session['userID'] = int(db.getUserID(request.form.get('User')))
            return redirect(url_for('search'))
        else:
            return render_template('login.html', failedLogin = True)

@app.route('/SignUp', methods=['GET','POST'])
def newUser():
    if request.method == 'POST':
        if db.addUser([request.form.get('User'), request.form.get('Email'), request.form.get('Password')]):
            return render_template('signup.html', success=0)
        else:
            return render_template('signup.html', success=-1)
    else:
        return render_template('signup.html', success=1)

@app.route('/Logout')
def logout():
    session['login'] = False
    session['userID'] = 0
    return redirect(url_for('search'))

def filterGenre(Genres, res):
    delList = []
    for i in res:
        add = True
        for j in Genres:
            if j in i['genre']:
                add = False
                break
        if (add):
            delList.append(i['imdb_title_id'])
    res[:] = [d for d in res if d['imdb_title_id'] not in delList]
    return res

def filterLanguage(Languages, res):
    delList = []
    for i in res:
        add = True
        for j in Languages:
            if j in i['language']:
                add = False
                break
        if (add):
            delList.append(i['imdb_title_id'])
    res[:] = [d for d in res if d['imdb_title_id'] not in delList]
    return res

@app.route('/process', methods=['GET','POST'])
def process():
    query = []
    res = ""
    query.append(int(request.json['yearStart']))
    query.append(int(request.json['yearEnd']))
    query.append(int(request.json['imdbStart']))
    query.append(int(request.json['imdbEnd']))

    Languages = []
    Genres = []
    Services = []
    if('languages' in request.json):
        Languages = [item for sublist in request.json['languages'] for item in sublist]
    if('genres' in request.json):
        Genres = [item for sublist in request.json['genres'] for item in sublist]
    if('streaming' in request.json):
        Services = [item for sublist in request.json['streaming'] for item in sublist]

    addLanguages = False
    addGenres = False
    addServices = False

    if(len(Languages) > 0 and len(Languages) < 19):
        addLanguages = True
    if(len(Genres) > 0 and len(Genres) < 17):
        addGenres = True
    if(len(Services)):
        addServices = True

    if(request.json['sorting'] == 'avg_vote'):
        if(addServices):
            res = db.filter_streaming(query, Services)
        else:
            res = db.filter_query(query)
        if(addGenres):
            res = filterGenre(Genres, res)
        if(addLanguages):
            res = filterLanguage(Languages, res)
        return render_template('results-mongo.html', results = res)
    elif(request.json['sorting'] == 'year'):
        if(addServices):
            res = db.filter_streaming_date(query, Services)
        else:
            res = db.filter_query_date(query)
        if(addGenres):
            res = filterGenre(Genres, res)
        if(addLanguages):
            res = filterLanguage(Languages, res)
        return render_template('results.html', results = res)
    else:
        if(addServices):
            res = db.filter_streaming_title(query, Services)
        else:
            res = db.filter_query_title(query)
        if(addGenres):
            res = filterGenre(Genres, res)
        if(addLanguages):
            res = filterLanguage(Languages, res)
        return render_template('results-mongo.html', results = res)


@app.route('/search', methods=['GET','POST'])   #MongoDB
def search():
    if request.method == 'GET':      
        if 'q' in request.args:
            term = request.args.get('q')
            category = request.args.get('c')
            res = ["No Matches Found"]
            print([term,category], file=sys.stderr)
            if category == "Cast/Crew Name":
                cursor = mongo_db.full_text_search_name(term)
                unique_res = set()
                for x in cursor:
                    unique_res.add(x['Name']) 
                res = list(unique_res)
            elif category == "Description":
                cursor = mongo_db.full_text_search_description(term)
                raw_res = []
                res = []
                if cursor:
                    for x in cursor:
                        raw_res.append((x["Imdb_Title_id"], x['title']))
                    for key, desc in raw_res:
                        t = mongo_db.query_by_id(key)
                        if t:
                            entry = t['title'] + ' : ' + desc + "\n"
                            res.append(entry)
            elif category == "Movie Title":
                cursor = mongo_db.full_text_search_title(term)
                unique_res = set()
                for x in cursor:
                    unique_res.add(x['title'])
                res = list(unique_res)
            return jsonify(matching_results=res)
        else:
            return render_template('base-test-nosql.html')
    else:
        print(request.json, file=sys.stderr)
        res = []
        if "searchTerm" in request.json:
            term = request.json['searchTerm']
            category = request.json['searchCategory']
            cursor = None
            if category == "Cast/Crew Name":
                cursor = mongo_db.query_person_titles(term)
            elif category == "Description":
                title = term.split(':')[0].strip()
                cursor = mongo_db.query_by_title_name(title)
            elif category == "Movie Title":
                cursor = mongo_db.query_by_title_name(term)
            else:   #category=="Search All"
                pass #TODO Setup multi-index text search       
            if cursor:
                res = [mov for mov in cursor]
            else:
                res = FAILURE
        else:
            print(request.json, file=sys.stderr)
            cursor = mongo_db.filter_query(request.json)
            res = [mov for mov in cursor]
        if not res:
            res = FAILURE
        return render_template('results-mongo.html', results = res)  


@app.route('/search/<moviename>')   #MongoDB
def search_title(moviename):
    imgurl = "https://moviebuffposters.blob.core.windows.net/images/" + moviename + ".jpg"
    request = requests.get(imgurl)
    if request.status_code != 200:
        imgurl = ''
    title = mongo_db.query_by_id(moviename)    
    title.pop("Imdb_Title_id")
    title.pop("_id")
    principals = title.pop("Principals")   
    cast_crew = []
    for role in principals:
        job = role["category"]
        names = role['name']
        for person in names:
            cast_crew.append((person["name"], job))
    return render_template('movie-nosql.html', res = json2html.convert(json=title), cast_crew = cast_crew, 
                        imgurl = imgurl, title = title['title'], titleId = moviename)

@app.route('/search/cast-crew/<name>')   #MongoDB
def search_person(name):
    person_details = mongo_db.query_by_person(name)
    print(person_details, file=sys.stderr)
    titles = mongo_db.query_person_titles(name)     #titles -> cursor object iterable
    person_all_roles = []
    person_title_role = {}
    for t in titles:       
        person_title_role = {"Imdb_Title_id": t["Imdb_Title_id"],
                            "title": t['title'],
                             "year": t['year']}
        principals = t["Principals"]
        for role in principals:
            names = role['name']
            print(names, file=sys.stderr)    
            for n in names:
                if n['name'] == name:
                    person_title_role.update({"category": role['category']})
                    print(person_title_role, file=sys.stderr)
                    person_all_roles.append(person_title_role)

    print(person_all_roles, file=sys.stderr)

    return render_template('person-mongo.html', title_details = person_all_roles, person = person_details)



@app.route('/<moviename>')
def movie(moviename):
    titleId = str(moviename)
    imgurl = "https://moviebuffposters.blob.core.windows.net/images/" + titleId + ".jpg"
    request = requests.get(imgurl)
    if request.status_code != 200:
        imgurl = ''
    dbRes = db.query_id(titleId)  
    if(dbRes):
        remove = []
        for i in dbRes.keys():
            if dbRes[i] == '':
                remove.append(i)
        for i in remove:
            del dbRes[i]
        nmRes = db.query_nm(str(moviename))
        names = dict()
        for i in nmRes:
            names[i['imdb_title_id']] = db.query_rName(str(i['imdb_title_id']))[0]['name']
        return render_template('movie.html', res = json2html.convert(json=dbRes), nmRes = nmRes, names = names, 
                        imgurl = imgurl, title = dbRes['title'], titleId = titleId)
    else:
        if res:
            #Testing: This title image verified in Datastore: try Intolerance (tt00006864)
            dbRes = res
            remove_fields = ["_id", "reviews_from_critics", "reviews_from_users",
                             "original_title", "date_published"]
            swaps = ["writer", "director", "actors"]
            cast_crew = {}

            for field in remove_fields:
                if field in dbRes:
                    dbRes.pop(field)
            for field in swaps:
                cast_crew[field] = dbRes.pop(field)
            for k,v in dbRes.items():
                if not v:
                    dbRes[k] = "N/A"
            
            nmRes = db.query_nm(str(moviename))
            names = dict()
            for i in nmRes:
                names[i['imdb_title_id']] = db.query_rName(str(i['imdb_title_id']))[0]['name']

        else:
            dbRes = FAILURE
            dbRes['imdb_title_id'] = moviename
        return render_template('movie.html', res = json2html.convert(json=dbRes), nmRes = nmRes, names = names, 
                        imgurl = imgurl, title = dbRes['title'], titleId = titleId)


@app.route('/<moviename>/reviews')
def reviews(moviename):
    titleId = str(moviename)
    imgurl = "https://moviebuffposters.blob.core.windows.net/images/" + titleId + ".jpg"
    request = requests.get(imgurl)
    if request.status_code != 200:
        imgurl = ''
    dbRes = db.query_id_reviews(titleId)
    reviewed = False
    avgScore = []
    for i in dbRes:
        if 'userID' in session and i['CreatedByUserID'] == session['userID']:
            reviewed = True
        avgScore.append(i['ReviewScore'])
    avgScoreFinal = 0
    if(len(avgScore)):
        avgScoreFinal = round(sum(avgScore) / len(avgScore), 1)
    return render_template('reviews.html', imgurl = imgurl, title = db.query_movieName(titleId)['title'], titleId = titleId, dbRes = dbRes, reviewed = reviewed, avgScore = avgScoreFinal)


@app.route('/<moviename>/reviews/create', methods=['GET','POST'])
def reviews_create(moviename):
    titleId = str(moviename)
    if request.method == 'GET':
        return render_template('reviews_create.html', title = db.query_movieName(titleId)['title'], titleId = titleId)

    elif request.method == 'POST':
        UserID = session['userID']
        Score = request.form.get("Score")
        Review = request.form.get("Review")
        db.create_review(UserID, Score, titleId, Review)
        return redirect(url_for('reviews', moviename=titleId))

@app.route('/<moviename>/reviews/<reviewId>/update', methods=['GET','POST'])
def reviews_update(moviename, reviewId):
    titleId = str(moviename)
    if request.method == 'GET':
        return render_template('reviews_update.html', title = db.query_movieName(titleId)['title'], titleId = titleId, reviewId = reviewId)
    elif request.method == 'POST':
        UserID = session['userID']
        Score = request.form.get("Score")
        Review = request.form.get("Review")
        db.update_review(Score, UserID, reviewId, Review)
        return redirect(url_for('reviews', moviename=titleId))
    

@app.route('/<moviename>/reviews/<reviewId>/delete', methods=['GET','POST'])
def reviews_delete(moviename, reviewId):
    titleId = str(moviename)
    
    if request.method == 'GET':
        dbRes = db.query_review_by_reviewid(reviewId)
        
        return render_template('reviews_delete.html', title = db.query_movieName(titleId)['title'], titleId = titleId, dbRes = dbRes)
    elif request.method == 'POST':
        db.remove_reviewtext_by_reviewid(reviewId)
        db.remove_review_by_reviewid(reviewId)
    
    return redirect(url_for('reviews', moviename=titleId))


@app.route('/_<personname>')
def person(personname):
    dbRes = db.query_nmData(str(personname))
    titleRes = dict()
    for i in dbRes:
        titleRes[i['imdb_name']] = db.query_movieName(i['imdb_name'])
    # print(dbRes, file=sys.stderr)
    # print(titleRes, file=sys.stderr)
    return render_template('person.html', dbRes = dbRes, titleRes = titleRes)



@app.route('/title-fetch/<title_id>', methods=['GET','POST'])
def cosmos_lookup():
    if request.method == 'GET':
        res = cosmos_db.query_enhanced(title_id)
        return render_template('basic-title-search.html')
    else:
        res = cosmos_db.query_enhanced(request.form['_id'])[0]
        return render_template('results.html', results = [res])


