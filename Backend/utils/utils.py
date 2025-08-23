import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

lemma = nltk.wordnet.WordNetLemmatizer()

def preprocess_text(text):
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [token for token in tokens if token not in stopwords.words('english')]
    punctuation_marks = ['.', ',', ';', '!', '?', ':', '-', '(', ')', '[', ']', '{', '}', "'", '"', '...', '—', "``", "''",'–', '/', '\\', '|', '$', '%', '^', '&', '*', '_', '~', '`', '<', '>']
    tokens = [lemma.lemmatize(token) for token in tokens if token not in punctuation_marks]
    return tokens