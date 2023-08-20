import openai
import pymysql
import re
import time
import os

# Set your OpenAI API key here
openai.api_key = os.environ['gpt_parser']

DB_HOST = 'localhost'
DB_NAME = 'gpt_parser'
USER_NAME = 'root'
PASSWORD = ''

conn = pymysql.connect(host=DB_HOST, user=USER_NAME, passwd=PASSWORD, db=DB_NAME, connect_timeout=5)

with conn.cursor() as cur:
    # SELECT COUNT(*) FROM `sentences` WHERE `ready` = '0'
    sql = "SELECT COUNT(*) FROM `sentences` WHERE `ready` = '0'"
    cur.execute(sql)
    result = cur.fetchall()
    for row in result:
        print(row)
        count = int(row[0])

    for i in range(count):
        # SELECT `id`, `sentence`, `sentence_web`, `id_text`, `order`, `ready` FROM `sentences` WHERE `ready` = '0' ORDER BY `id` ASC LIMIT 1
        sql = "SELECT `sentences`.`id`, `sentences`.`sentence`, `sentences`.`sentence_web`, `sentences`.`id_text`, \
         `sentences`.`order`, `sentences`.`ready`, `texts`.`language` FROM `sentences` LEFT JOIN `texts` \
         ON `sentences`.`id_text` = `texts`.`id` WHERE `sentences`.`ready` = '0' ORDER BY `sentences`.`id` ASC LIMIT 1"

        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            sentence_id = row[0]
            sentence = row[1]
            lang = row[6]

        sql = "SELECT `id`, `type`, `language`, `comand` FROM `gpt_comands` WHERE `language` = '%s' AND `type` = 'break_sentence'"
        sql = sql.replace("%s", str(lang))

        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            print(row)
            command = row[3]

        prompt = command + ': ' + sentence

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

        _sentences_parts = generated_text.split('\n')

        print(_sentences_parts)

        sentences_parts = []

        for sentences_part in _sentences_parts:
            sentences_part = sentences_part.strip()
            if len(sentences_part) == 0:
                continue
            if sentences_part[0] == '-' or sentences_part[0] == '•':
                sentences_part = sentences_part[1:].strip()
            else:
                sentences_part = re.sub(r'^\d+.', '', sentences_part).strip()

            if len(sentences_part) == 0:
                continue
            sentences_parts.append(sentences_part)

        sentences_parts.append(sentence)

        for sentences_part in sentences_parts:
            sentences_part = sentences_part.replace("'", "\\'")

            if ' ' not in sentences_part:
                continue

            # INSERT INTO `sentences_parts`(`parts`, `parts_web`, `id_sentence`) VALUES ('[value-1]','[value-2]','[value-3]')

            # INSERT INTO `sentences_parts`(`parts`, `parts_web`, `id_sentence`) VALUES ('%s','%s','%id')
            sql = "INSERT INTO `sentences_parts`(`parts`, `parts_web`, `id_sentence`) VALUES ('%s','%s','%id')"
            sql = sql.replace("%s", str(sentences_part))
            sql = sql.replace("%id", str(sentence_id))

            # print(sql)
            cur.execute(sql)
            conn.commit()
            print(str(cur.rowcount) + " Sentence part record(s) updated")

        #   UPDATE `sentences` SET `ready`='1' WHERE `id` = '%id'
        sql = "UPDATE `sentences` SET `ready`='1' WHERE `id` = '%id'"
        sql = sql.replace("%id", str(sentence_id))
        cur.execute(sql)
        conn.commit()
        print(str(cur.rowcount) + " Sentence record(s) updated")

        # exit()
