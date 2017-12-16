import re
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords


def text_preprocessing(
    text,
    remove_stopwords=False,
    stem_words=False,
    stopwords_addition=[],
    stopwords_exclude=[],
    HYPHEN_HANDLE=1
):
    """
    convert string text to lower and split into words.
    most punctuations are handled by replacing them with empty string.
    some punctuations are handled differently based on their occurences in the data.
    -  replaced with ' '
    few peculiar cases for better uniformity.
    'non*' replaced with 'non *'
    few acronyms identified
    SCID  Severe Combined ImmunoDeficiency
    ADA   Adenosine DeAminase
    PNP   Purine Nucleoside Phosphorylase
    LFA-1 Lymphocyte Function Antigen-1
    """
    text = text.lower().split()

    if remove_stopwords:
        stops = list(set(stopwords.words('english')) -
                     set(stopwords_exclude)) + stopwords_addition
        text = [w for w in text if w not in stops]

    text = " ".join(text)
    text = re.sub(r"[^A-Za-z0-9^,!.\/'+-=_]", " ", text)
    text = re.sub(r"(that|what)(\'s)", r"\g<1> is", text)
    text = re.sub(r"i\.e\.", "that is", text)
    text = re.sub(r"(^non| non)", r"\g<1> ", text)
    text = re.sub(r"(^anti| anti)", r"\g<1> ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r",", " ", text)
    text = re.sub(r"\.", " ", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\/", " ", text)
    text = re.sub(r"\^", " ^ ", text)
    text = re.sub(r"\+", " + ", text)
    if HYPHEN_HANDLE == 1:
        text = re.sub(r"\-", "-", text)
    elif HYPHEN_HANDLE == 2:
        text = re.sub(r"\-", " - ", text)
    text = re.sub(r"\=", " = ", text)
    text = re.sub(r"'", " ", text)
    re.sub(r"(\d+)(k)", r"\g<1>000", text)
    text = re.sub(r":", " : ", text)
    text = re.sub(r";", " ; ", text)
    text = re.sub(r" e g ", " eg ", text)
    text = re.sub(r" b g ", " bg ", text)
    text = re.sub(r"e - mail", "email", text)
    text = re.sub(r"\s{2,}", " ", text)

    text = text.lower().split()

    if remove_stopwords:
        stops = list(set(stopwords.words('english')) -
                     set(stopwords_exclude)) + stopwords_addition
        text = [w for w in text if w not in stops]

    text = " ".join(text)

    if stem_words:
        text = text.split()
        stemmer = SnowballStemmer('english')
        stemmed_words = [stemmer.stem(word) for word in text]
        text = " ".join(stemmed_words)

    # Return a list of words
    return(text)