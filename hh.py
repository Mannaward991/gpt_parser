import openai
import time
import os
import deepl


# Set your OpenAI API key here
openai.api_key = os.environ['gpt_parser']


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


# prompt = "Выбери все и только прилагательные из следуюшего текста так чтобы они не повторялись: \n \
# Жизнь прекрасна. Если ты умеешь жизнью наслаждаться, то она прекрасна. Если у тебя есть дело, \
# которое тебя интересует и в котором ты хочешь быть мастером, то ты можешь наслаждаться жизнью.  \
# Учиться любимому делу и заниматься им - это радость и наслаждение. Жизнь удивительна. Если ты \
# умеешь видеть новые вещи, то жизнь для тебя удивительна. Если у тебя есть тяга к познанию нового, \
# то ты можешь изучать новое бесконечно и это огромное удоволь ствие. Жизнь никогда не перестанет \
# удивлять тебя. Я очень хочу помочь людям разломать барьеры которые мешают им насла ждаться своей жизнью."


prompt = "Wähle alle nur die Adjektive aus dem folgenden Text so aus, dass sie sich nicht wiederholen: \n \
Das Leben ist schön. Wenn man weiß, wie man das Leben genießen kann, ist es schön. Wenn Sie ein Handwerk \
haben, das Sie interessiert und in dem Sie Meister werden wollen, können Sie das Leben genießen.  Einen \
Beruf zu erlernen, den man liebt, und ihn auszuüben, ist eine Freude und ein Vergnügen. Das Leben ist \
erstaunlich. Wenn Sie die Fähigkeit haben, neue Dinge zu sehen, dann ist das Leben für Sie erstaunlich. \
Wenn du den Drang hast, neue Dinge zu lernen, kannst du endlos neue Dinge lernen, und das ist ein großes \
Vergnügen. Das Leben wird nie aufhören, dich zu überraschen. Ich möchte den Menschen wirklich helfen, die \
Barrieren zu überwinden, die sie daran hindern, ihr Leben zu genießen."

# prompt = "Choose all and only the nouns from the following text so that they are not repeated: \n \
# Life is beautiful. If you know how to enjoy life, it is beautiful. If you have a business that interests \
# you and in which you want to be a master, you can enjoy life. Learning a work you love and doing it is a \
# joy and a pleasure. Life is amazing. If you have the ability to see new things, then life is amazing to you. \
# If you have an urge to discover new things, you can learn new things endlessly and it is a great pleasure. \
# Life will never stop surprising you. I really want to help people break down the barriers that prevent \
# them from enjoying their lives."

# prompt = "Choisissez tous et seulement les substantifs dans le texte suivant de manière à ce qu'ils ne se répètent pas: \n \
# La vie est belle. Si vous savez profiter de la vie, elle est belle. Si vous avez une activité qui vous intéresse \
# et dans laquelle vous voulez être maître, vous pouvez jouir de la vie.  Apprendre un métier que l'on aime et le \
# pratiquer est une joie et un plaisir. La vie est étonnante. Si vous avez la capacité de voir de nouvelles choses, \
# alors la vie est étonnante pour vous. Si vous avez envie d'apprendre de nouvelles choses, vous pouvez le faire \
# sans fin et c'est un grand plaisir. La vie ne cessera jamais de vous surprendre. Je veux vraiment aider les gens \
# à faire tomber les barrières qui les empêchent de jouir de leur vie."

# Generate text using the OpenAI API
response = openai.Completion.create(
    engine="text-davinci-003",  # You can choose the engine you want to use
    prompt=prompt,
    max_tokens=1000  # Adjust this parameter to control the length of the generated text
)

# Print the generated text
generated_text = response.choices[0].text.strip()

print(generated_text)

# prompt = "Поставь следующие прилагательные в единственное число мужского рода и именительный падеж: \n" + generated_text
prompt = "Setze folgenden Adjektive in den Singular mit männlicher Geschlechtsendung und in Nominativ: \n" + generated_text
# prompt = "Put following nouns in the singular: \n" + generated_text
# prompt = "Mettez les substantifs suivants au singulier et ajoutez l'article défini: \n" + generated_text

# Ждем 21 секунду. Лимит запросов 3 в минуту.
time.sleep(21)

# Generate text using the OpenAI API
response = openai.Completion.create(
    engine="text-davinci-003",  # You can choose the engine you want to use
    prompt=prompt,
    max_tokens=1000  # Adjust this parameter to control the length of the generated text
)

generated_text = response.choices[0].text.strip()

print(generated_text)

# Французско русские слова по первому тексту
# SELECT `texts_words`.`id_words_translation`, `words`.`word`, `words`.`word_web`, `translation`.`word`, `translation`.`word_web` FROM `texts_words` LEFT JOIN `words_translation` ON `texts_words`.`id_words_translation` = `words_translation`.`id` LEFT JOIN `words` ON `words_translation`.`id_word` = `words`.`id` LEFT JOIN `words` AS `translation` ON `words_translation`.`id_translation` = `translation`.`id` WHERE `texts_words`.`id_text` = '1' AND `words`.`language` = 'fr-FR' AND `translation`.`language` = 'ru-RU';
