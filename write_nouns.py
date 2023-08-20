import openai
import pymysql
import re
import time

# Set your OpenAI API key here
openai.api_key = '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'

DB_HOST = 'localhost'
DB_NAME = 'gpt_parser'
USER_NAME = 'root'
PASSWORD = ''


def has_dispersed_spaces(text, symbol, plus_count):
    words = text.replace(symbol, '')
    return len(text) > len(words) + plus_count


def first_letter_to_lower(text):
    if text:
        return text[0].lower() + text[1:]
    else:
        return text


conn = pymysql.connect(host=DB_HOST, user=USER_NAME, passwd=PASSWORD, db=DB_NAME, connect_timeout=5)

with conn.cursor() as cur:
    # SELECT COUNT(*) FROM `texts` WHERE `ready_words` = '0'
    sql = "SELECT COUNT(*) FROM `texts` WHERE `ready_words` = '0'"
    cur.execute(sql)
    result = cur.fetchall()
    for row in result:
        print(row)
        count = int(row[0])

    for i in range(count):

        sql = "SELECT `id`, `text`, `text_web`, `language`, `path`, `ready`, `ready_words` \
        FROM `texts` WHERE  `ready_words` = '0' ORDER BY `id` ASC LIMIT 1"

        cur.execute(sql)
        result = cur.fetchall()  # fetchall_unbuffered()
        for row in result:
            id_text = row[0]
            text = row[1]
            lang = row[3]

        sql = "SELECT `id`, `type`, `language`, `comand` FROM `gpt_comands` WHERE `language` = '%s' AND `type` = 'write_nouns_1'"
        sql = sql.replace("%s", str(lang))

        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            command = row[3]

        prompt = command + ': ' + text

        # Ждем 21 секунду. Лимит запросов 3 в минуту.
        time.sleep(21)

        # Generate text using the OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can choose the engine you want to use
            prompt=prompt,
            max_tokens=1000  # Adjust this parameter to control the length of the generated text
        )

        # Print the generated text
        generated_text = response.choices[0].text.strip()

        # print(generated_text)

        _sentences = generated_text.split('\n')
        for _sentence in _sentences:
            if has_dispersed_spaces(_sentence, ',', 0):
                #TODO убрать точку в конц предложения
                _words = _sentence.split(',')

        print(_words)

        words = []

        for word in _words:
            word = word.strip()
            if len(word) == 0:
                continue
            if word[0] == '-' or word[0] == '•':
                word = word[1:].strip()
            else:
                word = re.sub(r'^\d+.', '', word).strip()
            if len(word) == 0:
                continue
            word = first_letter_to_lower(word)
            words.append(word)

        for word in words:
            art_word = ''
            word_without_art = ''

            if lang == 'fr-FR':

                lll = 'l'
                article_resolution = ['le ', 'la ', 'un ', 'une ']
                no_article_resolution = ['les ', 'des ']

                for art in no_article_resolution:
                    if word.startswith(art):
                        art_word = art
                        word_without_art = word.replace(art, '')
                if art_word != '':
                    # Existe-t-il un singulier pour
                    prompt = "Existe-t-il un singulier pour" + ': ' + word
                    # Ждем 21 секунду. Лимит запросов 3 в минуту.
                    time.sleep(21)
                    # Generate text using the OpenAI API
                    response = openai.Completion.create(
                        engine="text-davinci-003",  # You can choose the engine you want to use
                        prompt=prompt,
                        max_tokens=1000  # Adjust this parameter to control the length of the generated text
                    )
                    generated_text = response.choices[0].text.strip()

                    # Non, en français, le mot "gens" n'a pas de forme singulière. Il est toujours utilisé au pluriel pour se référer à un groupe de personnes. Il n'y a pas d'équivalent singulier pour "gens" en français.
                    if word.startswith('Non,'):
                        pass

                    # Oui, en français, le singulier du mot "barrières" est "barrière". Donc, "barrière" est utilisé pour décrire une seule barrière, tandis que "barrières" est utilisé pour décrire plusieurs barrières.
                    if word.startswith('Oui,'):
                        # Ecrire le singulier avec l'article pour
                        prompt = "Ecrire le singulier avec l'article pour" + ': ' + word
                        # Ждем 21 секунду. Лимит запросов 3 в минуту.
                        time.sleep(21)
                        # Generate text using the OpenAI API
                        response = openai.Completion.create(
                            engine="text-davinci-003",  # You can choose the engine you want to use
                            prompt=prompt,
                            max_tokens=1000  # Adjust this parameter to control the length of the generated text
                        )
                        generated_text = response.choices[0].text.strip()
                        # Le singulier du mot "barrières" avec l'article est : "une barrière".
                        for art in article_resolution:
                            if '"' + art + word_without_art + '"' in generated_text:
                                art_word = art
                else:
                    for art in article_resolution:
                        if word.startswith(art):
                            art_word = art
                            word_without_art = word.replace(art, '')
            elif lang == 'de-DE':
                if word.startswith('eine '):
                    art_word = 'eine '
                    word_without_art = word.replace('eine ', '')
                elif word.startswith('ein '):
                    # Schreibe den bestimmten Artikel für den Nomen
                    prompt = "Schreibe den bestimmten Artikel für den Nomen" + ': ' + word  # TODO удалить запрос
                    # Ждем 21 секунду. Лимит запросов 3 в минуту.
                    time.sleep(21)
                    # Generate text using the OpenAI API
                    response = openai.Completion.create(
                        engine="text-davinci-003",  # You can choose the engine you want to use
                        prompt=prompt,
                        max_tokens=1000  # Adjust this parameter to control the length of the generated text
                    )
                    generated_text = response.choices[0].text.strip()
                    # Der bestimmte Artikel für das Substantiv "Beruf" im Deutschen ist "der". Also lautet der bestimmte Artikel für "Beruf" - "der Beruf".
                    # Der bestimmte Artikel für das Substantiv "Handwerk" im Deutschen ist "das". Also lautet der bestimmte Artikel für "Handwerk" - "das Handwerk".
                    for art in ['der ', 'das ']:
                        if '"' + art + word_without_art + '"' in generated_text:
                            art_word = art

                articles = ['der ', 'die ', 'das ']
                if art_word == '':
                    for art in articles:
                        if word.startswith(art):
                            art_word = art
                            word_without_art = word.replace(art, '')
            else:
                word_without_art = word

            word = word.replace("'", "\\'")

            # SELECT `id` FROM `words` WHERE `word` = ''
            sql = "SELECT `id` FROM `words` WHERE `word` = '%w'"
            sql = sql.replace("%w", word)

            id_w = False

            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                id_w = int(row[0])

            if not id_w or id_w == 0:
                # part_of_speech
                # 0 - другие 1 - существительное 2 - прилогательное 3 - глагол 4 - местоимение 5 - наречие 6 - предлоги 7 - союзы 8 - частицы 9 - междометия 10 - причастие 11 - диепричастие
                # INSERT INTO `words` (`word`, `word_web`, `language`, `part_of_speech`, `genus`) VALUES ('','','','','')
                sql = "INSERT INTO `words` (`word`, `word_web`, `language`, `part_of_speech`, `genus`) VALUES ('%w','%s','%l','%p','%g')"
                sql = sql.replace("%w", str(word))
                sql = sql.replace("%s", str(word_without_art))
                sql = sql.replace("%l", str(lang))
                sql = sql.replace("%p", str(1))
                if lang == 'fr-FR':
                    if art_word == 'le ' or art_word == 'un ':  # m ['le ', 'un ']
                        sql = sql.replace("%g", 'm')
                    elif art_word == 'la ' or art_word == 'une ':  # f ['la ', 'une ']
                        sql = sql.replace("%g", 'f')
                    elif art_word == 'les ' or art_word == 'des ':  # pl ['les ', 'des ']
                        sql = sql.replace("%g", 'pl')
                    else:
                        sql = sql.replace("%g", '')
                elif lang == 'de-DE':
                    if art_word == 'der ':
                        sql = sql.replace("%g", 'm')
                    elif art_word == 'die ':
                        sql = sql.replace("%g", 'f')
                    elif art_word == 'das ':
                        sql = sql.replace("%g", 'n')
                    else:
                        sql = sql.replace("%g", '')
                else:
                    sql = sql.replace("%g", '')
                print(sql)
                cur.execute(sql)
                conn.commit()

                # SELECT `id` FROM `words` WHERE `word` = ''
                sql = "SELECT `id` FROM `words` WHERE `word` = '%w'"
                sql = sql.replace("%w", word)

                cur.execute(sql)
                result = cur.fetchall()
                for row in result:
                    id_w = int(row[0])

            # INSERT INTO `words_buffer`(`word_id`, `text_id`, `sentences_id`, `language`) VALUES ('','','','')
            sql = "INSERT INTO `words_buffer`(`word_id`, `text_id`, `sentences_id`, `language`) VALUES ('%wi','%ti','%si','%l')"

            sql = sql.replace("%wi", str(id_w))
            sql = sql.replace("%ti", str(id_text))
            sql = sql.replace("%si", '')
            sql = sql.replace("%l", str(lang))

            cur.execute(sql)
            conn.commit()

        # UPDATE `sentences` SET `ready`='1' WHERE `id` = '%id'
        sql = "UPDATE `texts` SET `ready_words`='1' WHERE `id` = '%id'"
        sql = sql.replace("%id", str(id_text))
        cur.execute(sql)
        conn.commit()
        print(str(cur.rowcount) + " Sentence part record(s) updated")

        print(str(i) + '/' + str(count))

        exit()

