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


def split_text_by_symbols(text, split_symbols):
    split_pattern = f"([{re.escape(split_symbols)})]+)"
    sentences = re.split(split_pattern, text)
    result_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        if i < len(sentences) - 1:
            sentence = sentences[i] + sentences[i + 1]
            result_sentences.append(sentence)
        else:
            result_sentences.append(sentences[i])
    result_sentences = [sentence.strip() for sentence in result_sentences]
    result_sentences = [sentence for sentence in result_sentences if sentence.strip() != ""]
    return result_sentences


conn = pymysql.connect(host=DB_HOST, user=USER_NAME, passwd=PASSWORD, db=DB_NAME, connect_timeout=5)

with conn.cursor() as cur:
    # SELECT COUNT(*) FROM `sentences_parts` WHERE `ready` = '0'
    sql = "SELECT COUNT(*) FROM `sentences_parts` WHERE `ready` = '0'"
    cur.execute(sql)
    result = cur.fetchall()
    for row in result:
        print(row)
        count = int(row[0])

    for i in range(count):
        #
        sql = "SELECT `sentences_parts`.`id`, `sentences_parts`.`parts`, `sentences_parts`.`parts_web`, \
        `sentences_parts`.`id_sentence`, `sentences_parts`.`ready`, `sentences`.`id_text`, `texts`.`language` \
        FROM `sentences_parts` LEFT JOIN `sentences` ON `sentences_parts`.`id_sentence` = `sentences`.`id` \
        LEFT JOIN `texts` ON `sentences`.`id_text` = `texts`.`id` WHERE `sentences_parts`.`ready` = '0' \
        ORDER BY `sentences_parts`.`id` ASC LIMIT 1"

        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            sentences_parts_id = row[0]
            part = row[1]
            lang = row[6]

        # sql = "SELECT `id`, `type`, `language`, `comand` FROM `gpt_comands` WHERE `language` = '%s' AND `type` = 'make_phrases'"
        # sql = sql.replace("%s", str(lang))
        #
        # cur.execute(sql)
        # result = cur.fetchall()
        # for row in result:
        #     print(row)
        #     command = row[3]
        #
        # prompt = command + ': ' + part
        #
        # # Ждем 21 секунду. Лимит запросов 3 в минуту.
        # time.sleep(21)
        #
        # # Generate text using the OpenAI API
        # response = openai.Completion.create(
        #     engine="text-davinci-003",  # You can choose the engine you want to use
        #     prompt=prompt,
        #     max_tokens=1000  # Adjust this parameter to control the length of the generated text
        # )
        #
        # # Print the generated text
        # generated_text = response.choices[0].text.strip()
        #
        # # print(generated_text)
        #
        # _words_permutation = generated_text.split('\n')

        # print(_words_permutation)

        split_symbols = " "
        words = split_text_by_symbols(part, split_symbols)

        words_permutation = []
        str1 = ''

        for word in words:
            str1 = str1 + word
            words_permutation.append(str1)

        # for word_permutation in _words_permutation:
        #     word_permutation = word_permutation.strip()
        #     if len(word_permutation) == 0:
        #         continue
        #     if word_permutation[0] == '-' or word_permutation[0] == '•':
        #         word_permutation = word_permutation[1:].strip()
        #     else:
        #         word_permutation = re.sub(r'^\d+.', '', word_permutation).strip()
        #
        #     if len(word_permutation) == 0:
        #         continue
        #     words_permutation.append(word_permutation)

        # words_permutation =
        # words_permutation.append(part)

        for word_permutation in words_permutation:
            word_permutation = word_permutation.replace("'", "\\'")

            # INSERT INTO `words_permutation`(`permutation`, `permutation_web`, `id_part`) VALUES ('','','')
            sql = "INSERT INTO `words_permutation`(`permutation`, `permutation_web`, `id_part`) VALUES ('%s','%s','%id')"
            sql = sql.replace("%s", str(word_permutation))
            sql = sql.replace("%id", str(sentences_parts_id))

            # print(sql)
            cur.execute(sql)
            conn.commit()
            print(str(cur.rowcount) + " Permutation record(s) updated")

        #   UPDATE `sentences` SET `ready`='1' WHERE `id` = '%id'
        sql = "UPDATE `sentences_parts` SET `ready`='1' WHERE `id` = '%id'"
        sql = sql.replace("%id", str(sentences_parts_id))
        cur.execute(sql)
        conn.commit()
        print(str(cur.rowcount) + " Sentence part record(s) updated")

        print(str(i) + '/' + str(count))

        #exit()
