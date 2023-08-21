import openai
import pymysql
import re
import time
import os

# Set your OpenAI API key here
# openai.api_key = os.environ['gpt_parser']
openai.api_key = os.environ['gpt_parser_m']

DB_HOST = 'localhost'
DB_NAME = 'gpt_parser'
USER_NAME = 'root'
PASSWORD = ''

# UPDATE `texts` SET `ready_words`='0' WHERE `id` > '4'


def has_dispersed_spaces(text, symbol, plus_count):
    words = text.replace(symbol, '')
    return len(text) > len(words) + plus_count


def first_letter_to_lower(text):
    if text:
        return text[0].lower() + text[1:]
    else:
        return text


def get_command(_type, _lang, conn):
    with conn.cursor() as cur:
        sql = "SELECT `id`, `type`, `language`, `comand` FROM `gpt_comands` WHERE `language` = '%s' AND `type` = '%w'"
        sql = sql.replace("%s", str(_lang))
        sql = sql.replace("%w", str(_type))
        cur.execute(sql)
        _result = cur.fetchall()
        for row in _result:
            command = row[3]
        return command


def generated_text_to_words(generated_text):
    words = []
    _sentences = generated_text.split('\n')
    for _sentence in _sentences:
        if has_dispersed_spaces(_sentence, ',', 0):
            _sentence = _sentence.replace('.', '')
            for word in _sentence.split(','):
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
    return words


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

        prompt = get_command('write_verbs_1', lang, conn) + ': \n' + text
        # Ждем 21 секунду. Лимит запросов 3 в минуту.
        time.sleep(21)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000
        )
        generated_text_1 = response.choices[0].text.strip()

        print(generated_text_1)

        prompt = get_command('write_verbs_2', lang, conn) + ': \n' + generated_text_1
        # Ждем 21 секунду. Лимит запросов 3 в минуту.
        time.sleep(21)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000
        )
        generated_text = response.choices[0].text.strip()

        print(generated_text)

        words = generated_text_to_words(generated_text)

        print(words)

        new_words = []

        for word in words:
            word = word.replace("'", "\\'")
            new_words.append(word)

        for new_word in new_words:
            word = new_word

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
                sql = sql.replace("%s", str(word))
                sql = sql.replace("%l", str(lang))
                sql = sql.replace("%p", str(3))
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

            languages = ['ru-RU', 'de-DE', 'en-EN', 'fr-FR']
            for languag in languages:
                if languag == lang:
                    continue
                # INSERT INTO `words_buffer`(`word_id`, `text_id`, `language`) VALUES ('','','')
                sql = "INSERT INTO `words_buffer`(`word_id`, `text_id`, `language`) VALUES ('%wi', '%ti', '%l')"

                sql = sql.replace("%wi", str(id_w))
                sql = sql.replace("%ti", str(id_text))
                sql = sql.replace("%l", str(languag))

                print(sql)

                cur.execute(sql)
                conn.commit()

        # UPDATE `sentences` SET `ready`='1' WHERE `id` = '%id'
        sql = "UPDATE `texts` SET `ready_words`='1' WHERE `id` = '%id'"
        sql = sql.replace("%id", str(id_text))
        cur.execute(sql)
        conn.commit()
        print(str(cur.rowcount) + " Sentence part record(s) updated")

        print(str(i + 1) + '/' + str(count))

        # exit()

