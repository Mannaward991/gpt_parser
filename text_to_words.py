import pymysql
import re


DB_HOST = 'localhost'
DB_NAME = 'gpt_parser'
USER_NAME = 'root'
PASSWORD = ''


def number_of_unfinished_texts(conn):
    with conn.cursor() as cur:
        # SELECT COUNT(*) FROM `texts` WHERE `ready_words` = '6'
        sql = "SELECT COUNT(*) FROM `texts` WHERE `ready_words` < '6'"
        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            print(row)
            count = int(row[0])
        return count > 0


conn = pymysql.connect(host=DB_HOST, user=USER_NAME, passwd=PASSWORD, db=DB_NAME, connect_timeout=5)

with conn.cursor() as cur:

    while number_of_unfinished_texts(conn):

        # INSERT INTO `translation`(`word`, `translation`, `ready`) VALUES ('','','')

        sql = "SELECT `id`, `text`, `text_web`, `language`, `path`, `ready`, `ready_words` \
                FROM `texts` WHERE  `ready_words` < '6' ORDER BY `id` ASC LIMIT 1"

        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            text_id = row[0]
            text = str(row[1])

        re = ["\n", "\r"]
        for r in re:
            text = text.replace(r, '')

        re = [";", ":", ".", ",", "/", "?", "\"", "!", "-", "[", "]", "#",
              "$", "%", "^", "&", "*", "{", "}", "=", "_", "~", "(", ")"]  # "\\", "`", "'"
        for r in re:
            text = text.replace(r, '')

        text = text.replace("\\'", "'")
        text = text.replace("'", "\\'")

        words = text.split()
        unique_words_set = set(words)
        words = list(unique_words_set)

        for word in words:
            sql = "INSERT INTO `translation` (`word`) VALUES ('%w')"
            sql = sql.replace("%w", word)

            print(sql)

            cur.execute(sql)
            conn.commit()
            print("Added word " + word)

        sql = "UPDATE `texts` SET `ready_words`='6' WHERE `id` = '%id'"
        sql = sql.replace("%id", str(text_id))
        cur.execute(sql)
        conn.commit()
        print("Taxt id " + str(text_id) + " <<<<<<<<<<<<<<<<<<<<")
