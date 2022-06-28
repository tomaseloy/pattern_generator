from cgi import print_directory
import re
import spacy
import dateutil.parser as dparser
from datetime import datetime
from dateutil.relativedelta import *


class Tweet:
    def __init__(self, id_tweet, date, author, text, app, id_user, followers, following, stauses, location,	urls,	geolocation, RT_count,	favorite_count, url_media, type_media, quoted, relation, replied_id, user_replied, retweeted_id, user_retweeted, quoted_id, user_quoted, first_HT, lang, link, lugar_evento, fecha_evento):
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
        self.lugar_evento = lugar_evento
        self.fecha_evento = fecha_evento


def pertenece(autor, tweet):
    if(autor in tweet):
        return True
    return False


def filtro_palabras_clave(frase, palabras):
    for palabra in palabras:
        if palabra in frase:
            return True
    return False


def filtro_combinacion_palabras(frase, palabra):
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
    tweet = tweet.lower()  # pasa a minusculas
    return tweet


def detector_patron(patrones, texto):
    for patron in patrones:
        if re.search(patron, texto):
            return True
        return False


usuariosLista = []

with open("cuentasTwitterES.txt", encoding="ISO 8859-1") as usuarios:
    for usuario in usuarios:
        usuariosLista.append("@"+usuario.strip())


palabras_clave = ["partido", "encuentro", "manifestación",
                  "concentración", "obra", "obras", "concierto", "espectáculo", "presentación"]
contador = 0
lista_tweets = []
lista_tweets_cortada = []
filtrados = []
descartados = []

with open("tweets/suenosmusicales_tweets.txt", encoding="utf8") as tweets_txt:
    # pasamos los tweets a una lista
    for linea in tweets_txt:
        data = linea.split('\t')
        tweet = Tweet(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12], data[13],
                      data[14], data[15], data[16], data[17], data[18], data[19], data[20], data[21], data[22], data[23], data[24], data[25], data[26], None, None)
        lista_tweets.append(tweet)

# recortamos la lista a 1000 tweets/cuenta
lista_tweets = lista_tweets[1:1001]

# filtrar por palabras clave
for tweet in lista_tweets:
    if filtro_palabras_clave(tweet.text, palabras_clave):
        filtrados.append(tweet)
        # print(tweet.text)
    else:
        descartados.append(tweet)

# print(len(filtrados))
# print(len(descartados))

# PREPROCESADO
# eliminar los tweets que sean RT -> si user retweeted distinto de None es RT
no_RT_lista = []
for tweet in filtrados:
    if(tweet.user_retweeted == "None"):
        no_RT_lista.append(tweet)

# print(len(no_RT_lista))

# Eliminamos en cada tweet corchetes, los símbolos @ y #, símbolos de exclamación e interrogación, emoticonos y URLs.
for tweet in no_RT_lista:
    tweet.text = preprocesamiento(tweet.text)
    # print(tweet.text)

# usar https://spacy.io/, soporte para gallego: http://nlp.lsi.upc.edu/freeling/

nlp = spacy.load("es_core_news_sm")
for tweet in no_RT_lista:
    doc = nlp(tweet.text)

    print("********************************************")

    # detector de entidades con nombre
    for palabra in doc:
        print(palabra, palabra.pos_)

    print("********************************************")
    # detector de entidades con nombre
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.label_)


# Filtrado de tweets sin información necesaria de entidades Necesitamos tener información de localización (ciudad y calle) y de fecha

# es importante que sean loalizaciones de Santiago de Compostela en la presentación del proyecto
# puede ser muy eficiente extraer las localizaciones con el part of speech, o sacar los lugares de alguna lista externa
localizaciones = ["santiago bernabéu",
                  "pabellón caja rural", "teatralia", "teaprinalicante", "cartujacenter", "teatreechegaray"]
localizaciones_patrones = ["estadio", "sala",
                           "campo", "pabellón", "espectáculo", "concierto", "teatro"]
fechas = ["hoy", "mañana", "pasado mañana",
          "próxima semana", "siguiente semana", "mes", "año"]
fechas_patrones = []
tweetLocalizados = []
tweetLocalizadosConFecha = []
# lugares
for tweet in no_RT_lista:
    if filtro_palabras_clave(tweet.text, localizaciones):
        tweetLocalizados.append(tweet)
    elif filtro_palabras_clave(tweet.text, localizaciones_patrones):
        tweetLocalizados.append(tweet)
    else:
        descartados.append(tweet)
# print("Tweets: ", len(no_RT_lista))
# print("Tweets Localizados:  ", len(tweetLocalizados))
# print(tweetLocalizados[0].text)
# print(tweetLocalizados[1].text)
# print(tweetLocalizados[2].text)
# fechas
for tweet in tweetLocalizados:
    # print(tweet.text)
    if filtro_palabras_clave(tweet.text, fechas):
        tweetLocalizadosConFecha.append(tweet)
    else:
        try:  # formato numérico
            event_date = dparser.parse(tweet.text,
                                       fuzzy=True, dayfirst=True)
            tweetLocalizadosConFecha.append(tweet)

        except Exception:
            descartados.append(tweet)

print(len(tweetLocalizadosConFecha))
# print(tweetLocalizadosConFecha[0].text)

# Identificacion de patrones y extraccion de información relevante  *************************************NO ENTRA AQUI EL PROGRAMA**************************************
for tweet in tweetLocalizadosConFecha:
    # print(tweet.text)
    localizado = False
    for lugares in localizaciones:
        if filtro_combinacion_palabras(tweet.text, lugares):
            tweet.lugar_evento = lugares
            # print(tweet.location)
            localizado = True
        break

    for patrones in localizaciones_patrones:
        if not localizado:
            if filtro_combinacion_palabras(tweet.text, patrones):
                palabras = tweet.text.split(" ")
                patron = patrones.split(" ")
                ulitma_palabra_patron = patron[-1]
                # +1 para que no se incluya la palabra del patrón
                tweet.lugar_evento = palabras[palabras.index(patron[-1])+1]
                # print(tweet.location)
        break

# print(len(tweetLocalizadosConFecha))

for tweet in tweetLocalizadosConFecha:
    # tenemos que diferenciar en funcion de cada palabra clave
    if filtro_palabras_clave(tweet.text, fechas):
        for fecha in fechas:
            if(fecha == "hoy"):  # cambiar el today por la fecha del tweet
                tweet.fecha_evento = datetime.today().strftime("%d/%m/%Y")
                break

            elif(fecha == "pasado mañana"):
                tweet.fecha_evento = datetime.today() + relativedelta(days=2)
                tweet.fecha_evento = tweet.fecha_evento.strftime("%d/%m/%Y")
                break
            elif(fecha == "mañana"):
                tweet.fecha_evento = datetime.today() + relativedelta(days=1)
                tweet.fecha_evento = tweet.fecha_evento.strftime("%d/%m/%Y")
                break
            elif(fecha == "próxima semana" or fecha == "siguiente semana"):
                tweet.fecha_evento = datetime.today() + relativedelta(weeks=1)
                tweet.fecha_evento = tweet.date.strftime("%d/%m/%Y")
                break
            elif(fecha == "mes"):
                tweet.fecha_evento = datetime.today() + relativedelta(months=1)
                tweet.fecha_evento = tweet.date.strftime("%d/%m/%Y")
                break
            elif(fecha == "año"):
                tweet.fecha_evento = datetime.today() + relativedelta(year=1)
                tweet.fecha_evento = tweet.date.strftime("%d/%m/%Y")
            else:
                break

    else:
        try:  # formato numérico
            event_date = dparser.parse(tweet.text,
                                       fuzzy=True, dayfirst=True)
            tweet.fecha_evento = event_date

        except Exception:
            print("Error")

for tweet in tweetLocalizadosConFecha:
    print("********************************************")
    print(tweet.fecha_evento, " ", tweet.lugar_evento)
    print(tweet.text)


# PENDIENTE
# - clasificar por cuentas
# - crear patrones y palabras para sacar informacion de lugar y fecha para todas las cuentas
# - organizar mejor el código

# NEXT
# - crear patrones para cada cuenta
# buscar tweets con tres elementos interesantes a identifcar:
# 1.palabra claves, entidades
# 2.fecha
# 3.localizacion
# ademas  CONECTORES(verbos o preposiciones)
#     ejemplo: el dia(fecha)17 juega(conector verbo) el madrid(nada) en(prep conector) santander(localizacion)
# ciertas partes del texto reconocibles, y ciertos huecos, buscamos los puntos entre parentesis, | fecha "formato" |-| verbo "jugar"|-| prep "en" |-| localizacion "santander" |-> tweet patron

# puede haber patrones parecidos pero no iguales, en los que cambia o falta algo,
# Puede haber un patron originado por tweet, o patron generado por varios tweets similares, normalmente se relacionan por los conectores,

# USAR CUENTA (p.e.: @cgm_madrid enfocará mas obras, pero está bien) CON VARIOS EVENTOS PARA PROBAR DEPURAR LA HERRAMIENTA DE EXTRACCION DE PATRONES, lo + importante es coger muchos patrones,
# da igual si muchos son malos, con un 30% de acierto sirve(% validado por el cliente)

listaPatrones = []

# IDEAS
# se podria hacer uso del part of speech para sacar los conectores(verbos o preposiciones)
#   -> sobretodo podria rentar para hacer una lista de verbos(principalmente) y preposiciones personalizados para cada cuenta, y asi lograr una implementacion + general y daria un mejor y uso del part of speech

#   tipo, si tenemos este verbo, + tal preposicion, tenemos ya un patron utilizable (pueden ser necesario más de un conector tipo prep),
#   ya se veria despues como acabar el patron, que en pricnipio seria una suma de los conectores(100%) + palabras clave(50%)


def identificadorPatrones(lista_tweets):
    # identificar patrones
    # 1. palabras claves
    # 2. fecha
    # 3. localizacion
    # 4. conector
    # 5. cuenta
    # 6. palabras claves y fecha
    # 7. palabras claves y localizacion
    # 8. palabras claves y conector
    # 9. fecha y localizacion
    # 10. fecha y conector
    # 11. localizacion y conector
    # 12. palabras claves, fecha y localizacion
    # 13. palabras claves, fecha y conector
    # 14. palabras claves, localizacion y conector
    # 15. fecha, localizacion y conector
    # 16. palabras claves, fecha, localizacion y conector
    # 17. palabras claves, cuenta
    # 18. palabras claves, cuenta y fecha
    # 19. palabras claves, cuenta y localizacion
    # 20. palabras claves, cuenta y conector
    # 21. palabras claves, fecha, cuenta
    # 22. palabras claves, fecha, cuenta y localizacion
    # 23. palabras claves, fecha, cuenta y conector
    # 24. palabras claves, localizacion, cuenta
    # 25. palabras claves, localizacion, cuenta y fecha
    # 26. palabras claves, localizacion, cuenta y conector
    # 27. palabras claves, fecha, localizacion, cuenta
    # 28. palabras claves, fecha, localizacion, cuenta y conector
    # 29. palabras claves, fecha, localizacion, cuenta y conector
    # 30. palabras claves, localizacion, cuenta, fecha y conector
    # 31. palabras claves, cuenta, fecha, localizacion y conector
    for tweet in tweetLocalizadosConFecha:
        if(re.search("en", tweet) and re.search(fecha, tweet) and re.search(localizaciones, tweet)):
            print("Identificado patron tipo 1")
            print(tweet.text)
