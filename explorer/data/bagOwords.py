# based on algorithm by Mikolov, T., Chen, K., Corrado, G.S., & Dean, J. (2013). Efficient Estimation of Word Representations in Vector Space. CoRR, abs/1301.3781.
# cited by Moshe Hazoom published on Dec 22, 2018 @ https://towardsdatascience.com/word2vec-for-phrases-learning-embeddings-for-more-than-one-word-727b6cf723cf
# import re
# from spacy.lang.en.stop_words import STOP_WORDS
# from gensim.models.phrases import Phrases, Phraser

# def get_sentences(input_file_pointer):
#     while True:
#         line = input_file_pointer.readline()
#         if not line:
#             break

#         yield line


# def clean_sentence(sentence):
#     sentence = sentence.lower().strip()
#     sentence = re.sub(r'[^a-z0-9\s]', '', sentence)
#     return re.sub(r'\s{2,}', ' ', sentence)

# def tokenize(sentence):
#     return [token for token in sentence.split() if token not in STOP_WORDS]
    

# def build_phrases(sentences):
#     phrases = Phrases(sentences,
#                       min_count=5,
#                       threshold=7,
#                       progress_per=1000)
#     return Phraser(phrases)

# phrases_model.save('phrases_model.txt')
# phrases_model= Phraser.load('phrases_model.txt')

# def sentence_to_bi_grams(phrases_model, sentence):
#     return ' '.join(phrases_model[sentence])

# def sentences_to_bi_grams(n_grams, input_file_name, output_file_name):
#     with open(input_file_name, 'r') as input_file_pointer:
#         with open(output_file_name, 'w+') as out_file:
#             for sentence in get_sentences(input_file_pointer):
#                 cleaned_sentence = clean_sentence(sentence)
#                 tokenized_sentence = tokenize(cleaned_sentence)
#                 parsed_sentence = sentence_to_bi_grams(n_grams, tokenized_sentence)
#                 out_file.write(parsed_sentence + '\n')

# sentences_to_bi_grams(["minsky"], './docs1-all-text.txt', './hello.txt')


# load data
import sys
folder = './explorer/data/'
filename = folder+sys.argv[1]
file = open(filename, 'rt')
text = file.read()
file.close()

# split into words
from nltk.tokenize import word_tokenize
tokens = word_tokenize(text)

# convert to lower case
tokens = [w.lower() for w in tokens]

# remove punctuation from each word
import string
table = str.maketrans('', '', string.punctuation)
stripped = [w.translate(table) for w in tokens]

# remove remaining tokens that are not alphabetic
words = [word for word in stripped if word.isalpha()]

# filter out stop words
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
words = [w for w in words if not w in stop_words]

# remove duplicates and count frequency
unique = {}
for word in words:
    if not word in unique:
        unique[word] = 1
    else:
        unique[word]+=1
       
# todo sort the dictionary by value - Greatest to Least (last time I tried that, it removed words with the same number of occurances.)

# output the dictionary to file
outFile = open(folder+"vec-"+sys.argv[1], 'w')
for k,v in unique.items():
    outFile.write((k+", "+str(v)+",\n"))
outFile.close()