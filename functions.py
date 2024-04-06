# Fichero: functions.py
# Autor: Tomás Eloy Suárez Martínez
# Descripción: Funciones de utilidad para el proceso de extracción de patrones

import re

def keywords_filter(phrase, words):
    """
    keywords_filter(phrase, words)

    Comprueba si alguna de las palabras de la lista `words` se encuentra en la frase `phrase`.

    Parametros
    ----------
        `phrase`: cadena de texto

        'words': listado de palabras

    Devuelve:
    ----------
           La función devuleve 'True' o 'False' dependiendo de si alguna de las palabras de la lista `words` se encuentra en la frase `phrase`.
    """
    phrase = phrase.lower()
    for word in words:
        if word in phrase:
            return True
    return False

def remove_emoji(string):
    """
    remove_emoji(string)

    Elimina los emoticonos de una cadena de texto `string`.

    Parametros
    ----------
        `string`: cadena de texto

    Devuelve:
    ----------
           La función devuleve la cadena de texto `string` sin emoticonos.
    """
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
                               u"\u20e3"
                               u"\u2139"
                               u"\u203c"
                               u"\u2066"
                               u"\u2069"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def preprocessing(tweet):
    """
    preprocessing(tweet)

    Preprocesa una cadena de texto `tweet` eliminando caracteres especiales, emoticonos, url, etc.

    Parametros
    ----------
        `tweet`: cadena de texto

    Devuelve:
    ----------
           La función devuleve la cadena de texto `tweet` preprocesada.
    """
    tweet = remove_emoji(tweet)
    # tweet = re.sub(r'[^\w\s]', '', tweet)
    # Eliminate duplicate whitespaces
    tweet = re.sub(r'\s+', ' ', tweet)
    # elimina caracteres especiales
    tweet = re.sub(r"\[|\]|\@|\#|\?|\¿|\¡|\!|\||\(|\)|\+", "", tweet)
    tweet = re.sub(r'http\S+', '', tweet)   # elimina url
    # tweet = tweet.lower()  # pasa a minusculas
    return tweet

def replace_word(text, word_search, word_replace):
    """
    replace_word(text, word_search, word_replace)

    Reemplaza una palabra por otra en una cadena de texto `text`.

    Parametros
    ----------
        `text`: cadena de texto

        `word_search`: palabra a buscar

        'word_replace': palabra por la que se reemplaza

    Devuelve:
    ----------
           La función devuleve la cadena de texto `text` con la palabra reemplazada.
    """
    split_text = text.split()
    for i in range(len(split_text)):
        if split_text[i] == word_search:
            split_text[i] = word_replace
    return " ".join(split_text)

def date_finder(text):
    """
    date_finder(text)

    Busca fechas en una cadena de texto.

    Parametros
    ----------
        `text`: cadena de texto

    Devuelve:
    ----------
        `dates`: lista con las fechas encontradas
    """

    '''
    'date_pattern' recoge fechas en los siguientes formatos :
    1. (?:hasta el\s+)?\d{1,2} de [a-z]+(?: de \d{4})?                              - (hasta el) 12 de septiembre (de 2023)
    2. \d{1,2}\s*-\s*\d{1,2}\s+de\s+[a-z]+(?: de \d{4})?                            - 1-15 de octubre (de 2023)
    3. \d{1,2} y (?:el )?\d{1,2} de [a-z]+(?: de \d{4})?                            - 3 y 5 de noviembre (de 2023)
    4. \d{1,2}/\d{1,2}(?:/\d{2,4})?                                                 - 25/12(/2023)
    5. \d{1,2} al \d{1,2} de [a-z]+                                                 - 8 al 12 de diciembre
    6. \d{1,2} de [a-z]+ al \d{1,2} de [a-z]+                                       - 5 de marzo al 10 de marzo
    '''
    date_pattern = r"(?:hasta el\s+)?\d{1,2} de [a-z]+(?: de \d{4})?|\d{1,2}\s*-\s*\d{1,2}\s+de\s+[a-z]+(?: de \d{4})?|\d{1,2} y (?:el )?\d{1,2} de [a-z]+(?: de \d{4})?|\d{1,2}/\d{1,2}(?:/\d{2,4})?|\d{1,2} al \d{1,2} de [a-z]+|\d{1,2} de [a-z]+ al \d{1,2} de [a-z]+"

    dates = re.findall(date_pattern, text)
    return dates

def select_adjacent_words(text, categories_list, window_size):
    """
    select_adjacent_words(text, categories_list, window_size)

    Selecciona las palabras adyacentes a una lista de palabras en una cadena de texto.

    Parametros
    ----------
        `text`: cadena de texto

        `categories_list`: lista de palabras

        `window_size`: tamaño de la ventana (número de palarbas adyacentes a seleccionar)

    Devuelve:
    ----------
        `selected_words`: lista con las palabras adyacentes a la lista de palabras
    """
    selected_words = []
    words = text.split()
    posiciones = [i for i, p in enumerate(words) if p in categories_list]
    for index in posiciones:
        selected_words.append(words[index+window_size] + " " + words[index])
    return selected_words

def tweet_pattern_selector(text, pattern):
    """
    tweet_pattern_selector(text, pattern))

    Comprueba si el texto `text` coincide con el patrón `pattern`.

    Parametros
    ----------
        `text`: cadena de texto

        `pattern`: patrón

    Devuelve:
    ----------
        La función devuleve 'True' o 'False' dependiendo de si el texto `text` coincide con el patrón `pattern`.
    """
    # remplazar todos los {} por \{\}
    pattern_re = []
    for word in pattern:
        word = re.sub("{", "\{", word)
        word = re.sub("}", "\}", word)
        pattern_re.append(word)
    regular_expression = ""
    for combination in pattern_re:
        if regular_expression != "":
            regular_expression = regular_expression + ".*" + combination
        else:
            regular_expression = combination

    # Comprobar resultados
    coincidences = re.findall(regular_expression, text)
    if coincidences:
        return True
    else:
        return False