import openai
import pymysql
import re
import os

# Set your OpenAI API key here
openai.api_key = os.environ['gpt_parser']

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
    # SELECT `id`, `text`, `text_web`, `language`, `path`, `ready` FROM `texts` WHERE  `ready` = '0' ORDER BY `id` ASC LIMIT 1
    sql = "SELECT `id`, `text`, `text_web`, `language`, `path`, `ready` FROM `texts` WHERE  `ready` = '0' ORDER BY `id` ASC LIMIT 1"
    # sql = sql.replace("%s", str(id_start))
    cur.execute(sql)
    result = cur.fetchall()  # fetchall_unbuffered()
    for row in result:
        print(row)
        id_text = row[0]
        text = row[1]
        lang = row[3]

    # sql = "SELECT `id`, `type`, `language`, `comand` FROM `gpt_comands` WHERE `language` = '%s' AND `type` = 'break_text'"
    # sql = sql.replace("%s", str(lang))

    # cur.execute(sql)
    # result = cur.fetchall()
    # for row in result:
    #     print(row)
    #     command = row[3]

    # exit()
    # Prompt for text generation
    # prompt = "Décomposez le texte suivant en phrases: La vie est belle. Si vous savez jouir de la vie, elle est belle. Si vous avez une activité qui vous intéresse et dans laquelle vous voulez être maître, vous pouvez jouir de la vie.  Apprendre un métier que l\'on aime et le pratiquer est une joie et un plaisir. La vie est étonnante. Si vous avez la capacité de voir de nouvelles choses, alors la vie est étonnante pour vous. Si vous avez envie d\'apprendre de nouvelles choses, vous pouvez apprendre de nouvelles choses sans fin et c\'est un grand plaisir. Je veux vraiment aider les gens à faire tomber les barrières qui les empêchent de jouir de leur vie."
    # prompt = command + ': ' + text

    # Generate text using the OpenAI API
    # response = openai.Completion.create(
        # engine="text-davinci-003",  # You can choose the engine you want to use
        # prompt=prompt,
        # max_tokens=1000  # Adjust this parameter to control the length of the generated text
    # )

    # Print the generated text
    # generated_text = response.choices[0].text.strip()

    # print(generated_text)

    # _sentences = generated_text.split('\n')
    split_symbols = ".!?"
    _sentences = split_text_by_symbols(text, split_symbols)

    print(_sentences)

    # sentences = []
    #
    # for sentence in _sentences:
    #     sentence = sentence.strip()
    #     if len(sentence) == 0:
    #         continue
    #     if sentence[0] == '-' or sentence[0] == '•':
    #         sentence = sentence[1:].strip()
    #     else:
    #         sentence = re.sub(r'^\d+.', '', sentence).strip()
    #
    #     if len(sentence) == 0:
    #         continue
    #     sentences.append(sentence)

    order = 1
    for sentence in _sentences:
        sentence = sentence.replace("'", "\\'")
        # INSERT INTO `sentences`(`sentence`, `sentence_web`, `id_text`, `order`) VALUES ('%s','%s2','%idt','%i')
        sql = "INSERT INTO `sentences`(`sentence`, `sentence_web`, `id_text`, `order`) VALUES ('%s','%s','%idt','%i')"
        sql = sql.replace("%s", str(sentence))
        sql = sql.replace("%idt", str(id_text))
        sql = sql.replace("%i", str(order))

        # print(sql)
        cur.execute(sql)
        conn.commit()
        print(str(cur.rowcount) + " Sentence record(s) updated")
        order = order + 1

    # UPDATE `texts` SET `ready`='1' WHERE `id` = '%id'
    sql = "UPDATE `texts` SET `ready`='1' WHERE `id` = '%id'"
    sql = sql.replace("%id", str(id_text))
    cur.execute(sql)
    conn.commit()
    print(str(cur.rowcount) + " Text record(s) updated")


