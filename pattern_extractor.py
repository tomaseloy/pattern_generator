# Fichero: pattern_extractor.py
# Autor: Tomás Eloy Suárez Martínez
# Descripción: Funciones para generar los patrones de una cuenta

import spacy
import re
import os
import functions

# Clase que representa un patrón
class Patron:
    def __init__(self, patron_completo, patron_recortado, puntuacion, tweet_ejemplo1, tweet_ejemplo2):
        self.patron_completo = patron_completo
        self.patron_recortado = patron_recortado
        self.puntuacion = puntuacion
        self.tweet_ejemplo1 = tweet_ejemplo1
        self.tweet_ejemplo2 = tweet_ejemplo2

def get_patterns(author, tweets_list):
    """
    get_patterns(author, tweets_list)

    Genera los patrones de cada cuenta a partir de sus 1000 últimos tweets y los almacena en un fichero .txt
    Los patrones incluyen información sobre eventos, fechas y localizaciones: {EVENT}, {DATE}, {LOCATION}
    
    Parametros
    ----------
        `author`: nombre de la cuenta de la que se van a generar los patrones

        `tweets_list`: listado de tweets de la cuenta

    """
    keywords = ["partidos", "partido", "encuentros", "encuentro", "manifestaciones", "manifestación",
                    "concentración", "obras", "obra", "conciertos", "concierto", "espectáculos", "espectáculo", "presentaciones", "presentación"]
    
    dates = ["hoy", "mañana", "pasado mañana"]

    weekdays = ["lunes", "martes", "miércoles",
                "jueves", "viernes", "sábado", "domingo"]

    categories = ["{EVENT}", "{DATE}", "{LOCATION}"]
    
    filtereds = []
    # filtrar por palabras clave
    for tweet in tweets_list:
        if functions.keywords_filter(tweet.text, keywords):
            filtereds.append(tweet)

    # PREPROCESADO DE DATOS
    # Eliminamos en cada tweet corchetes, los símbolos @ y #, símbolos de exclamación e interrogación, emoticonos y URLs.
    for tweet in filtereds:
        tweet.text_modified = functions.preprocessing(tweet.text)

    nlp = spacy.load("es_core_news_sm")

    tweet_sust_loc = []
    tweet_sust_eve = []
    tweet_sust = []
    substituted_tweets_list = []

    for tweet in filtereds:
        doc = nlp(tweet.text_modified)
        # detector de entidades con nombre
        for ent in doc.ents:
            if(ent.label_ == "LOC"):
                if ent.text.split() == 1:
                    tweet.text_modified = functions.replace_word(
                        tweet.text_modified, ent.text, "{LOCATION}")
                else:
                    tweet.text_modified = tweet.text_modified.replace(
                        ent.text, "{LOCATION}")
        tweet_sust_loc.append(tweet)

    for tweet in tweet_sust_loc:
        # pasamos a minusculas el texto
        tweet.text_modified = tweet.text_modified.lower()
        for word in keywords:
            if word in tweet.text_modified:
                tweet.text_modified = functions.replace_word(
                    tweet.text_modified, word, "{EVENT}")
        tweet_sust_eve.append(tweet)

    for tweet in tweet_sust_eve:
        tweet.text_modified = re.sub(
            "{location}", "{LOCATION}", tweet.text_modified)

        # quitamos palabras innecesarias para el patron(dias semana)
        for word in weekdays:
            if word in tweet.text_modified:
                tweet.text_modified = re.sub(word+" ", "",
                                                tweet.text_modified)

            # método que localiza fechas y las sustituye por su categoria {DATE}
            dates_found = functions.date_finder(tweet.text_modified)
            if dates_found:
                for date in dates_found:
                    if "hasta" in date:
                        tweet.text_modified = re.sub(
                            date, "hasta {DATE}", tweet.text_modified)
                    else:
                        tweet.text_modified = re.sub(
                            date, "{DATE}", tweet.text_modified)
                tweet_sust.append(tweet)
            else:
                if functions.keywords_filter(tweet.text_modified, dates):
                    for word in dates:
                        if word in tweet.text_modified:
                            tweet.text_modified = functions.replace_word(
                                tweet.text_modified, word, "{DATE}")
                            tweet_sust.append(tweet)

    # filtrar tweets que no contengan todos los elementos
    for tweet in tweet_sust:
        if "{EVENT}" in tweet.text_modified and "{LOCATION}" in tweet.text_modified and "{DATE}" in tweet.text_modified:
            substituted_tweets_list.append(tweet)

     # Formación patrones
    selected_pattern_list = []
    selected_pattern_neg_list = []
    pattern_list = []

    # PATRON POR TAMAÑO VENTANA {palabras colindantes con los datos relevantes}
    for tweet in substituted_tweets_list:
        tweet.text_modified = re.sub(r'["\'\.,:-]', '', tweet.text_modified)
        pattern = ""

        pattern_words = functions.select_adjacent_words(
            tweet.text_modified, categories, -1)

        if(pattern_words != None):
            pattern_list.append(
                Patron(tweet.text, tweet.text_modified, pattern_words, None, None, None))

    pattern_list_no_rep_tmp = []
    pattern_list_no_rep = []

    # eliminamos patrones repetidos
    for pattern in pattern_list:
        if pattern.full_pattern not in pattern_list_no_rep_tmp:
            pattern_list_no_rep_tmp.append(pattern.full_pattern)
            pattern_list_no_rep.append(pattern)

    complete_pattern_list = []
    for pattern in pattern_list_no_rep:
        # eliminamos patrones que no contengan alguna palabra de la lista de categorias
        str_pattern = str(pattern.full_pattern)
        if "{EVENT}" in str_pattern and "{DATE}" in str_pattern and "{LOCATION}" in str_pattern:
            complete_pattern_list.append(pattern)
    

    # seleccionamos los mas relevantes (PATRONES CANDIDATOS)-> mediante formula
    for pattern in complete_pattern_list:

        cant_tweets_rel = 0
        cant_tweets_tot = 0
        for tweet in substituted_tweets_list:
            tweet_included_rel = False
            if functions.tweet_pattern_selector(tweet.text_modified, pattern.full_pattern):
                tweet_included_rel = True
            if tweet_included_rel:
                cant_tweets_rel = cant_tweets_rel+1
                if(pattern.sample_tweet1 == None):
                    pattern.sample_tweet1 = re.sub(r'\n', ' ', tweet.text)
                elif(pattern.sample_tweet2 == None and pattern.sample_tweet1 != tweet.text):
                    pattern.sample_tweet2 = re.sub(r'\n', ' ', tweet.text)

        pattern.punctuation = cant_tweets_rel

        # print("PUNTUACION TOTAL:", cant_tweets_tot,
        #       "PUNTUACION RELEVANTE:", cant_tweets_rel)
        # print("PUNTUACION MEDIA:", res)


    complete_pattern_list.sort(key=lambda x: x.puntuacion, reverse=True)

  # Validación por parte del usuario
    print("Se han generado los siguientes patrones: ", len(complete_pattern_list))
    for pattern in complete_pattern_list:
        if(pattern.punctuation > 0):
            print("")
            print("Patron: ", pattern.full_pattern)
            print(" - Puntuacion: ", pattern.punctuation)
            print(" - Tweet inicial: ", pattern.tweet_init)
            print(" - Tweet origen: ", pattern.tweet_source)
            print(" - Tweet ejemplo 1: ", pattern.sample_tweet1)
            print(" - Tweet ejemplo 2: ", pattern.sample_tweet2)

            print(
                "Si considera que el patrón es válido inserte la letra -s-, en caso negativo inserte -n-")
            validation = input()
            if(validation == "s" or validation == "S"):
                print("Patrón agregado")
                selected_pattern_list.append(pattern)
            elif(validation == "n" or validation == "N"):
                print("Patrón descartado")
            elif(validation == "close" or validation == "CLOSE"):
                print("Selección de patrones cortada, cerrando aplicación...")
                break
            else:
                print("TECLA EQUIVOCADA, Por favor, escriba -s- o -n-")
    

    print("Los patrones finales son: ")
    for pattern in selected_pattern_list:
        print("Patron: ", pattern.full_pattern)

    # escribir patrones en un fichero .txt
    try:
        os.mkdir("../accounts/"+author)
        # os.mkdir("accounts/"+author)
    except:
        pass
    file = open("../accounts/"+author +
                "/patterns.txt", "a", encoding="utf8")
    # file = open("accounts/"+author +
    #             "/patterns.txt", "a", encoding="utf8")
    for pattern in selected_pattern_list:
        pattern_str = ", ".join(pattern.full_pattern)
        file.write(pattern_str + "\n")
    file.close()
    print("Patrones almacenados en patterns.txt")

if __name__ == "__main__":
    author = "" # Añadir nombre de la cuenta
    tweets_list = [] # Añadir lista con últimos tweets de la cuenta
    get_patterns(author, tweets_list)