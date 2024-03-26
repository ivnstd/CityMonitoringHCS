from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, NewsSyntaxParser, AddrExtractor, Doc

segmenter = Segmenter()
morph_vocab = MorphVocab()
addr_extractor = AddrExtractor(morph_vocab)

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)

week_words = ['Саратов', 'Саратова', 'Энгельс', 'Энгельса']

problems_dictionary = {
    'Водоснабжение': ['водоснабжение', 'вода'],
    'Теплоснабжение': ['отопление', 'горячий'],
    'Электроснабжение': ['электричество', 'свет'],
    'Дорожное снабжение': ['асфальт', 'яма']
}


def get_address(text):
    """ Извлечение адреса из текста """
    address_list = []
    matches = addr_extractor(text)
    objects = [i.fact.as_json for i in matches]

    # Цикл для вывода адреса в удобной форме
    for object in objects:
        address_list.extend(list(object.values()))
    address = " ".join(address_list)

    # Проверка на значительность полученного адреса
    if len(address_list) > 2 or len(address_list) == 2 and not any(word in address for word in week_words):
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
