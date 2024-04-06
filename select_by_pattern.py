# Fichero: select_by_pattern.py
# Autor: Tomás Eloy Suárez Martínez
# Descripción: Filtra los tweet que publican las cuentas a las que se quiere hacer seguimiento.
#  Si un tweet encaja con alguno de los patrones generados previamente para la propia cuenta, se muestra por pantalla la información del evento.

import re
import spacy
import functions

def tweet_filter(tweet, author):
    """
    tweet_filter(tweet, author)

    Filtra los tweets que publican las cuentas a las que se hace seguimiento.
    Si un tweet encaja con alguno de los patrones generados previamente para la propia cuenta, se muestra por pantalla la información del evento.

    Parametros
    ----------
        `tweet`: texto del tweet

        `author`: nombre de la cuenta que ha publicado el tweet
    """
    keywords  = ["partidos", "partido", "encuentros", "encuentro", "manifestaciones", "manifestación",
                    "concentración", "obras", "obra", "conciertos", "concierto", "espectáculos", "espectáculo", "presentaciones", "presentación"]

    dates  = ["hoy", "mañana", "pasado mañana"]

    weekdays = ["lunes", "martes", "miércoles",
                "jueves", "viernes", "sábado", "domingo"]
    
    type_event = None
    place_event = None
    date_event = None
    text_modified = ""
    pattern_list = []

    print("TWEET ORIGEN: " + tweet)

    with open("accounts/" + author + "/patterns.txt") as patterns:
        # pasamos los patrones a una lista
        for line in patterns:
            pattern_list.append(line)

    # Eliminamos en cada tweet corchetes, los símbolos @ y #, símbolos de exclamación e interrogación, emoticonos y URLs.
    text_modified = functions.preprocessing(tweet)

    
    # Detector de entidades con nombre
    nlp = spacy.load("es_core_news_sm")
    doc = nlp(text_modified)

    # Localizamos el token {LOCATION}
    for ent in doc.ents:
        if(ent.label_ == "LOC"):
            text_modified = re.sub(ent.text, "{LOCATION}", text_modified)
            if place_event == None:
                place_event = ent.text
            else:
                place_event = place_event + " - " + ent.text
    

    # Pasamos a minusculas el texto
    text_modified = text_modified.lower()
    text_modified = re.sub("{location}", "{LOCATION}", text_modified)
    # Quitamos signos de puntuación
    text_modified = re.sub("[\.\,\:\-\“\”]", "", text_modified)

    # Localizamos el token {EVENT}
    for word in keywords:
        if word in text_modified:
            text_modified = re.sub(word, "{EVENT}", text_modified)
            if type_event == None:
                type_event = word
            else:
                type_event = type_event + ", " + word

     # Quitamos palabras innecesarias para el patron(dias semana)
    for word in weekdays:
        if word in text_modified:
            text_modified = re.sub(word+" ", "",
                                   text_modified)
            
    # Localizamos el token {DATE}
    dates = functions.date_finder(text_modified)
    if dates:
        for date in dates:
            if "hasta" in date:
                text_modified = re.sub(
                    date, "hasta {DATE}", tweet)
            else:
                text_modified = re.sub(date, "{DATE}", text_modified)

            if date_event == None:
                date_event = date
            else:
                date_event = date_event + ", " + date
    else:
        if functions.keywords_filter(text_modified, dates):
            for word in dates:
                if word in text_modified:
                    text_modified = re.sub(
                        " "+word+" ", " {DATE} ", text_modified)
                    date_event = word
                    break

    final_pattern_list = []

    for pattern in pattern_list:
        modified_pattern = re.sub("\n", "", pattern)
        modified_pattern = modified_pattern.split(", ")
        final_pattern_list.append(modified_pattern)

    print("")
    print("TWEET MODIFICADO: " + text_modified)
    print("")

    finally_selected = False
    # Seleccionamos los tweets que coincidan con alguno de los patrones obtenidos de la cuenta
    for pattern in final_pattern_list:
        selected = functions.tweet_pattern_selector(text_modified, pattern)

        if selected:
            print("Tweet -SI- seleccionado")
            print("Patrón: " + str(pattern))
            finally_selected = True
            break

    if not finally_selected:
        print("Tweet -NO- seleccionado")

    if finally_selected:
        print("")
        # eliminamos los saltos de linea (si los hubiera)
        place_event = re.sub("\n", "", place_event)

        print("Datos del evento:")
        print("Tipo evento: ", type_event)
        print("Localización: ", place_event)
        print("Fecha: ", date_event)

if __name__ == "__main__":
    tweet = ""  # Tweet a procesar
    author = "" # Cuenta que ha publicado el tweet
    tweet_filter(tweet, author)