import re
import spacy


class Tweet:
    def __init__(self, id_tweet, date, author, text, app, id_user, followers, following, stauses, location,	urls,	geolocation, RT_count,	favorite_count, url_media, type_media, quoted, relation, replied_id, user_replied, retweeted_id, user_retweeted, quoted_id, user_quoted, first_HT, lang, link):
        self.id_tweet = id_tweet
        self.date = date
        self.author = author
        self.text = text
        self.app = app
        self.id_user = id_user
        self.followers = followers
        self.following = following
        self.stauses = stauses
        self.location = location
        self.urls = urls
        self.geolocation = geolocation
        self.RT_count = RT_count
        self.favorite_count = favorite_count
        self.url_media = url_media
        self.type_media = type_media
        self.quoted = quoted
        self.relation = relation
        self.replied_id = replied_id
        self.user_replied = user_replied
        self.retweeted_id = retweeted_id
        self.user_retweeted = user_retweeted
        self.quoted_id = quoted_id
        self.user_quoted = user_quoted
        self.first_HT = first_HT
        self.lang = lang
        self.link = link


def pertenece(autor, tweet):
    if(autor in tweet):
        return True
    return False


def filtro_palabras_clave(frase, palabras):
    for palabra in palabras:
        if palabra in frase:
            return True
    return False


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u'\U00010000-\U0010ffff'
                               u"\u200d"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\u3030"
                               u"\ufe0f"
                               u"\u23f0"
                               u"\u23f3"
                               u"\ufe0f"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def preprocesamiento(tweet):
    tweet = remove_emoji(tweet)
    tweet = re.sub(r'[^\w\s]', '', tweet)
    tweet = re.sub(r'\s+', ' ', tweet)
    # elimina caracteres especiales
    tweet = re.sub("\[|\]|\@|\#|\?|\¿|\¡|\!|\|", "", tweet)
    tweet = re.sub(r'http\S+', '', tweet)   # elimina url
    #tweet = tweet.lower()
    return tweet


def detector_patron(patron, texto):
    if re.search(patron, texto):
        return True
    return False


# primero hay que separar para cada cuenta
# usuariosCoUNT=0
usuariosLista = []
# cuenta0=[]
# cuenta1=[]
# cuenta2=[]
# cuenta3=[]
# cuenta4=[]
# cuenta5=[]
# cuenta6=[]
# cuenta7=[]
# cuenta8=[]
# cuenta9=[]

with open("cuentasTwitterES.txt", encoding="utf8") as usuarios:
    for usuario in usuarios:
        usuariosLista.append("@"+usuario.strip())

# with open("wlist_tweets.txt", encoding="utf8") as tweets_txt:
#   for tweet in tweets_txt:
#     # print(tweet)
#     if pertenece(usuariosLista[0], tweet):
#       cuenta0.append(tweet)

#     elif pertenece(usuariosLista[1], tweet):
#       cuenta1.append(tweet)

#     elif pertenece(usuariosLista[2], tweet):
#       cuenta2.append(tweet)

#     elif pertenece(usuariosLista[3], tweet):
#       cuenta3.append(tweet)

#     elif pertenece(usuariosLista[4], tweet):
#       cuenta4.append(tweet)

#     elif pertenece(usuariosLista[5], tweet):
#       cuenta5.append(tweet)

#     elif pertenece(usuariosLista[6], tweet):
#       cuenta6.append(tweet)

#     elif pertenece(usuariosLista[7], tweet):
#       cuenta7.append(tweet)

#     elif pertenece(usuariosLista[8], tweet):
#       cuenta8.append(tweet)

#     elif pertenece(usuariosLista[9], tweet):
#       cuenta9.append(tweet)

#     else:
#       print("No pertenece a ninguna cuenta")

# print(cuenta9)

palabras_clave = ["partido", "encuentro", "manifestación",
                  "concentración", "obra", "obras", "concierto", "espectáculo"]
contador = 0
lista_tweets = []
lista_tweets_cortada = []
filtrados = []
descartados = []

with open("realmadrid.txt", encoding="utf8") as tweets_txt:
    # pasamos los tweets a una lista
    for linea in tweets_txt:
        data = linea.split('\t')
        tweet = Tweet(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12], data[13],
                      data[14], data[15], data[16], data[17], data[18], data[19], data[20], data[21], data[22], data[23], data[24], data[25], data[26])
        lista_tweets.append(tweet)

# recortamos la lista a 1000 tweets/cuenta
# lista_tweets_cortada = lista_tweets[1:1001]

# filtrar por palabras clave
for tweet in lista_tweets:
    if filtro_palabras_clave(tweet.text, palabras_clave):
        filtrados.append(tweet)
    else:
        descartados.append(tweet)

# print(len(lista_tweets_cortada))
# print(lista_tweets_cortada[0])
# print(len(filtrados))
# print(len(descartados))

# PREPROCESADO
# eliminar los tweets que sean RT -> si user retweeted distinto de None es RT
no_RT_lista = []
for tweet in filtrados:
    if(tweet.user_retweeted == "None"):
        no_RT_lista.append(tweet)

# print(len(no_RT_lista))
# print(no_RT_lista[9].text)
# Eliminamos en cada tweet corchetes, los símbolos @ y #, símbolos de exclamación e interrogación, emoticonos y URLs.

for tweet in no_RT_lista:
    tweet.text = preprocesamiento(tweet.text)

# print(no_RT_lista[9].text)
# detector de entidades con nombre y categorías gramaticales ->  POS (part-of-speech)
# print(no_RT_lista[6].text)
# usar https://spacy.io/, soporte para gallego: http://nlp.lsi.upc.edu/freeling/

nlp = spacy.load("es_core_news_sm")
for tweet in no_RT_lista:
    doc = nlp(tweet.text)

    # print("********************************************")

    # detector de entidades con nombre
    # for palabra in doc:
    #print(palabra, palabra.pos_)

    # print("********************************************")
    # detector de entidades con nombre
    # for ent in doc.ents:
    #print(ent.text, ent.start_char, ent.end_char, ent.label_)


# Filtrado de tweets sin información necesaria de entidades Necesitamos tener información de localización (ciudad y calle) y de fecha


# es importante que sean loalizaciones de Santiago de Compostela en la presentación del proyecto
localizaciones = ["Santiago Bernabéu"]
fechas = ["hoy", "mañana", "pasado mañana", "mes"]
tweetLocalizados = []
tweetLocalizadosConFecha = []
# lugares
for tweet in no_RT_lista:
    if filtro_palabras_clave(tweet.text, localizaciones):
        tweetLocalizados.append(tweet)
    else:
        descartados.append(tweet)

# print(len(descartados))
# print(tweetLocalizados[0])

# fechas
for tweet in tweetLocalizados:
    if filtro_palabras_clave(tweet.text, fechas):
        tweetLocalizadosConFecha.append(tweet)
    else:
        descartados.append(tweet)

# print(len(tweetLocalizadosConFecha))
# print(tweetLocalizadosConFecha[0])

# Identificacion de patrones y extraccion de información relevante
for tweet in tweetLocalizadosConFecha:
    if(detector_patron("mañana un homenaje ", tweet.text)):
        words = tweet.text.split(" ")
        print(words[words.index("homenaje")+2])

        # PENDIENTE
        # como detectar fechas en textos -> mirar en internet
        # - clasificar por cuentas
        # - crear patrones y palabras para sacar informacion de lugar y fecha para todas las cuentas
        # - organizzar mejor el código
