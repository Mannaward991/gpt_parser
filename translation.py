import openai
import pymysql
import re
import os
import deepl

# Set your OpenAI API key here
# openai.api_key = os.environ['gpt_parser']
openai.api_key = os.environ['gpt_parser_m']

DB_HOST = 'localhost'
DB_NAME = 'gpt_parser'
USER_NAME = 'root'
PASSWORD = ''


def add_translation(word, lang_from, lang_to):

    # Text translation options
    # In addition to the input text(s) argument, the available translate_text() arguments are:
    #
    # source_lang: Specifies the source language code, but may be omitted to auto-detect the source language.
    # target_lang: Required. Specifies the target language code.
    # split_sentences: specify how input text should be split into sentences, default: 'on'.
    # 'on'' (SplitSentences.ON): input text will be split into sentences using both newlines and punctuation.
    # 'off' (SplitSentences.OFF): input text will not be split into sentences. Use this for applications where each input text contains only one sentence.
    # 'nonewlines' (SplitSentences.NO_NEWLINES): input text will be split into sentences using punctuation but not newlines.
    # preserve_formatting: controls automatic-formatting-correction. Set to True to prevent automatic-correction of formatting, default: False.
    # formality: controls whether translations should lean toward informal or formal language. This option is only available for some target languages, see Listing available languages.
    # 'less' (Formality.LESS): use informal language.
    # 'more' (Formality.MORE): use formal, more polite language.
    # glossary: specifies a glossary to use with translation, either as a string containing the glossary ID, or a GlossaryInfo as returned by get_glossary().
    # tag_handling: type of tags to parse before translation, options are 'html' and 'xml'.
    # The following options are only used if tag_handling is 'xml':
    #
    # outline_detection: specify False to disable automatic tag detection, default is True.
    # splitting_tags: list of XML tags that should be used to split text into sentences. Tags may be specified as an array of strings (['tag1', 'tag2']), or a comma-separated list of strings ('tag1,tag2'). The default is an empty list.
    # non_splitting_tags: list of XML tags that should not be used to split text into sentences. Format and default are the same as for splitting_tags.
    # ignore_tags: list of XML tags that containing content that should not be translated. Format and default are the same as for splitting_tags.
    # For a detailed explanation of the XML handling options, see the API documentation.

    auth_key = os.environ['deepl_gpt_parser']
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(
        word,
        source_lang=lang_from,  # 'DE'
        target_lang=lang_to,  # 'RU'
        split_sentences='nonewlines'
        # formality='less'
    )
    translator.close()
    return result.text


def target_lang_to_supported_from(lang):
    if lang == 'ru-RU':
        return 'RU'
    elif lang == 'fr-FR':
        return 'FR'
    elif lang == 'en-EN':
        return 'EN'
    elif lang == 'de-DE':
        return 'DE'


def target_lang_to_supported_to(lang):
    if lang == 'ru-RU':
        return 'RU'
    elif lang == 'fr-FR':
        return 'FR'
    elif lang == 'en-EN':
        return 'EN-GB'
    elif lang == 'de-DE':
        return 'DE'


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


def number_of_unfinished_texts(conn):
    with conn.cursor() as cur:
        # SELECT COUNT(*) FROM `texts` WHERE `ready_words` = '4'
        sql = "SELECT COUNT(*) FROM `texts` WHERE `ready_words` = '4'"
        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            print(row)
            count = int(row[0])
        return count > 0


conn = pymysql.connect(host=DB_HOST, user=USER_NAME, passwd=PASSWORD, db=DB_NAME, connect_timeout=5)

with conn.cursor() as cur:

    while number_of_unfinished_texts(conn):

        sql = "SELECT `id`, `text`, `text_web`, `language`, `path`, `ready`, `ready_words` \
                FROM `texts` WHERE  `ready_words` = '4' ORDER BY `id` ASC LIMIT 1"

        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            text_id = row[0]
            text = row[1]
            lang = row[3]

        # sql = "SELECT `texts_translation`.`id_text`, `texts_translation`.`id_translation`, `texts`.`language` \
        # FROM `texts_translation` LEFT JOIN `texts` on `texts_translation`.`id_translation` = `texts`.`id` \
        # WHERE `texts_translation`.`id_text` = '%id'"
        # sql = sql.replace("%id", text_id)
        #
        # all_texts_id = []
        #
        # cur.execute(sql)
        # result = cur.fetchall()
        # for row in result:
        #     all_texts_id.append({'id_text': })

        languages = ['ru-RU', 'de-DE', 'en-EN', 'fr-FR']

        for lang_to in languages:

            if lang_to == lang:
                continue

            # findet text_id_to
            sql = "SELECT `texts_translation`.`id_translation`, `texts`.`language` FROM `texts_translation` \
            LEFT JOIN `texts` ON `texts_translation`.`id_translation` = `texts`.`id` WHERE \
            `texts_translation`.`id_text` = '%id' AND `texts`.`language` = '%la'"
            sql = sql.replace("%id", str(text_id))
            sql = sql.replace("%la", str(lang_to))

            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                text_id_to = row[0]

            words_to = []

            # findet all words text_id_to
            sql = "SELECT DISTINCT `words_buffer`.`word_id`, `words`.`word`, `words`.`word_web` \
            FROM `words_buffer` LEFT JOIN `words` ON `words`.`id` = `words_buffer`.`word_id` \
            WHERE `words_buffer`.`text_id` = '%id'"
            sql = sql.replace("%id", str(text_id_to))

            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                words_to.append({
                    'word_id': row[0],
                    'word': row[1],
                    'word_web': row[2]
                })

            # all words of the current text
            sql = "SELECT `words_buffer`.`id`, `words_buffer`.`word_id`, `words_buffer`.`text_id`, \
            `words_buffer`.`language`, `words`.`word`, `words`.`word_web`, `words`.`part_of_speech` \
            FROM `words_buffer` LEFT JOIN `words` ON `words_buffer`.`word_id` = `words`.`id` \
            WHERE `words_buffer`.`text_id` = '%id' AND `words_buffer`.`language` = '%la'"
            sql = sql.replace("%id", str(text_id))
            sql = sql.replace("%la", str(lang_to))

            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                buffer_id = row[0]
                word_id = row[1]
                word = row[4]
                word_web = row[5]
                part_of_speech = row[6]

                fin = False

                if word == '':
                    if word_web == '':
                        continue
                    else:
                        translation = add_translation(word_web, target_lang_to_supported_from(lang), target_lang_to_supported_to(lang_to))
                else:
                    translation = add_translation(word, target_lang_to_supported_from(lang),target_lang_to_supported_to(lang_to))

                translation = translation.replace("'", "\\'")
                translation = translation.replace("\n", '')

                for word_to in words_to:
                    if translation == word_to['word'] or translation == word_to['word_web']:
                        # нашли совпадение

                        sql = "INSERT INTO `words_translation`(`id_word`, `id_translation`) VALUES ('%id','%t')"
                        sql = sql.replace("%id", str(word_id))
                        sql = sql.replace("%t", str(word_to['word_id']))
                        cur.execute(sql)
                        conn.commit()
                        # print(str(cur.rowcount) + " Sentence record(s) updated")

                        sql = "INSERT INTO `words_translation`(`id_word`, `id_translation`) VALUES ('%id','%t')"
                        sql = sql.replace("%id", str(word_to['word_id']))
                        sql = sql.replace("%t", str(word_id))
                        cur.execute(sql)
                        conn.commit()

                        sql = "SELECT `id` FROM `words_translation` WHERE `id_word` = '%id' AND `id_translation` = '%t'"
                        sql = sql.replace("%id", str(word_id))
                        sql = sql.replace("%t", str(word_to['word_id']))

                        cur.execute(sql)
                        result = cur.fetchall()
                        for row in result:
                            words_translation_id_1 = row[0]

                        sql = "SELECT `id` FROM `words_translation` WHERE `id_word` = '%id' AND `id_translation` = '%t'"
                        sql = sql.replace("%id", str(word_to['word_id']))
                        sql = sql.replace("%t", str(word_id))

                        cur.execute(sql)
                        result = cur.fetchall()
                        for row in result:
                            words_translation_id_2 = row[0]

                        sql = "INSERT INTO `texts_words`(`id_text`, `id_words_translation`) VALUES ('%id','%t')"
                        sql = sql.replace("%id", str(text_id))
                        sql = sql.replace("%t", str(words_translation_id_1))
                        cur.execute(sql)
                        conn.commit()

                        sql = "INSERT INTO `texts_words`(`id_text`, `id_words_translation`) VALUES ('%id','%t')"
                        sql = sql.replace("%id", str(text_id_to))
                        sql = sql.replace("%t", str(words_translation_id_2))
                        cur.execute(sql)
                        conn.commit()

                        # delete from words_buffer  buffer_id
                        sql = "DELETE FROM `words_buffer` WHERE `id` = '%id'"
                        sql = sql.replace("%id", str(buffer_id))
                        cur.execute(sql)
                        conn.commit()

                        # delete from words_buffer  text_id_to lang word_id
                        sql = "DELETE FROM `words_buffer` WHERE `text_id` = '%ti' AND `language` = '%l' AND `word_id` = '%wi'"
                        sql = sql.replace("%ti", str(text_id_to))
                        sql = sql.replace("%l", str(lang))
                        sql = sql.replace("%wi", str(word_id))
                        cur.execute(sql)
                        conn.commit()

                        fin = True

                if not fin:
                    # не нашли совпадение

                    # SELECT `id` FROM `words` WHERE `word` = ''
                    sql = "SELECT `id` FROM `words` WHERE `word` = '%w'"
                    sql = sql.replace("%w", str(translation))

                    new_word_id = False

                    cur.execute(sql)
                    result = cur.fetchall()
                    for row in result:
                        new_word_id = int(row[0])

                    if not new_word_id or new_word_id == 0:

                        sql = "INSERT INTO `words`(`word`, `word_web`, `language`, `part_of_speech`, `genus`) VALUES ('%wm','%ww','%l','%p','')"
                        sql = sql.replace("%wm", str(translation))
                        sql = sql.replace("%ww", str(translation))
                        sql = sql.replace("%l", str(lang_to))
                        sql = sql.replace("%p", str(part_of_speech))
                        print(sql)
                        cur.execute(sql)
                        conn.commit()

                        sql = "SELECT `id` FROM `words` WHERE `word` = '%wm' AND `word_web` = '%ww' AND `language` = '%l' \
                        AND `part_of_speech` = '%p' ORDER BY `id` DESC LIMIT 1"
                        sql = sql.replace("%wm", str(translation))
                        sql = sql.replace("%ww", str(translation))
                        sql = sql.replace("%l", str(lang_to))
                        sql = sql.replace("%p", str(part_of_speech))
                        print(sql)
                        cur.execute(sql)
                        result = cur.fetchall()
                        for row in result:
                            new_word_id = row[0]

                    sql = "INSERT INTO `words_translation`(`id_word`, `id_translation`) VALUES ('%id','%t')"
                    sql = sql.replace("%id", str(word_id))
                    sql = sql.replace("%t", str(new_word_id))
                    print(sql)
                    cur.execute(sql)
                    conn.commit()

        sql = "UPDATE `texts` SET `ready_words`='5' WHERE `id` = '%id'"
        sql = sql.replace("%id", str(text_id))
        cur.execute(sql)
        conn.commit()
        print(str(cur.rowcount) + " Sentence part record(s) updated")