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

def natasha_analysis(text):
    address, problem = [], []
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)

    # Разбиение текста на леммы
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    lemmas = list({_.text: _.lemma for _ in doc.tokens}.values())

    for problem_type in problems_dictionary.keys():
        if any([sign in lemmas for sign in problems_dictionary[problem_type]]):
            problem.append(problem_type)

    # if problem:
    # Извлечение адреса из текста
    matches = addr_extractor(text)
    objects = [i.fact.as_json for i in matches]
    # Цикл для вывода адреса в удобной форме
    for object in objects:
        address.extend(list(object.values()))

    return address, problem


def text_analysis(text):
    """
        Анализ сообщений:
        выделение в каждом сообщении адреса и проблемы
    """
    (address, problem) = natasha_analysis(text)
    # if problem:
    address_str = " ".join(address)
    # if len(address) > 3 or len(address) == 3 and not any(word in address_str for word in week_words):
    for problem_type in problem:
        return address_str, problem_type

# messages = [
#     "ул. Днепропетровская, 2 ( обновлено)",
#     "Здравствуйте. Работы по расчистке дороги по ул. Южной проводились. Дополнительная расчистка включена в план. О заснеженных и скользких участках, где требуется провести расчистку, можно сообщать нам в личные сообщения или по телефону 96-07-70.",
#     "Уважаемая Администрация Ленинского района, когда же уже будет счищена колея во дворе дома Тархова 21??? Приехала с работы, как была колея, так и есть! 2 недели отписок! БАРДАК!",
#     "Для ликвидации повреждения водопровода по ул.Лунная, 2/6 сегодня, 01 июля, ориентировочно до 20.00 ограничено холодное водоснабжение абонентов ул.Лунная (от Деловой до Вишневой)"
# ]
def processing(text):
    try:
        # Вызываем обработку текста - извлечение из сообщения
        # адреса и проблемы, если они есть
        address, problem = text_analysis(text)

        return address, problem


    except:
        # Обработка исключения в случае, если сообщение не удалось
        # обработать по непредусмотренным причинам, например,
        # наличия символов другой кодировки
        print(f"Не удалось обработать сообщение с text:")
        return None, None

