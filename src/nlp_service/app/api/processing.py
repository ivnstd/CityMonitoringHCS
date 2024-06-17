from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, NewsSyntaxParser, AddrExtractor, Doc
import re


segmenter = Segmenter()
morph_vocab = MorphVocab()
addr_extractor = AddrExtractor(morph_vocab)

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)


problems_dictionary = {
    'Теплоснабжение': ['отопление', 'горячий'],
    'Электроснабжение': ['электричество', 'свет'],
    'Дорожное хозяйство': ['асфальт', 'яма'],
    'Водоснабжение': ['водоснабжение', 'вода'],
    'Вывоз ТБО': ['мусор', 'баки', 'контейнер', 'свалка', 'уборка'],
}

home_matches = r'(,\s?)?(д\. |д |дом. )?(\d+(/\d+)?[\s]?([А-Яа-я])?)($|\s|\b)'
street_matches = r'(ул\. |ул |улиц. )?((\d+(-?[а-я]*)\s)?[А-Я][А-я-]*)'


def get_home(text, street=None):
    template = home_matches
    if street:
        template = street + ',*\s+' + home_matches

    home = re.findall(template, text)

    def home_match_value(match):
        match_value = 0
        for i in range(len(match) - 1):
            if match[i]:
                match_value += 1
                if i == 0:
                    match_value += 1
                if i == 1:
                    match_value += 2
        return match_value

    if home:
        max_match_home = max(home, key=home_match_value)
        return max_match_home[2]


def get_street(text, home=None):
    template = street_matches
    if home:
        template = street_matches + '(,?\s?[а-я]*\s*)' + home

    street = re.findall(template, text)

    def street_match_value(match):
        match_value = 0
        for i in range(len(match)):
            if match[i]:
                match_value += 1
                if i == 0:
                    match_value += 2
        return match_value

    if street:
        max_match_home = max(street, key=street_match_value)
        return max_match_home[1]


def get_address(text):
    """ Извлечение адреса из текста """
    address_list = []
    street = ""
    home = ""

    matches = addr_extractor(text)
    objects = [i.fact.as_json for i in matches]

    # Извлечение адреса
    for object in objects:
        try:
            typ = object["type"]
            val = object["value"]

            if typ == "улица":
                street = val
            elif typ == "дом":
                home = val

            address_list.extend([typ, val])
        except Exception:
            address_list.append(object["value"])

    if not home:
        home = get_home(text)
    if not street and home:
        street = get_street(text, home)
    elif not home and street:
        home = get_home(text, street)

    if street and "улица" not in address_list:
        address_list.extend(["улица", street])
    if home and "дом" not in address_list:
        address_list.extend(["дом", home])

    address = " ".join(address_list)

    # Проверка на значительность полученного адреса
    if len(address_list) > 2:
        return address


def get_problem(text):
    """ Извлечение проблемы из текста """
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)

    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    lemmas = list({_.text: _.lemma for _ in doc.tokens}.values())

    for problem_type in problems_dictionary.keys():
        if any([sign in lemmas for sign in problems_dictionary[problem_type]]):
            return problem_type
