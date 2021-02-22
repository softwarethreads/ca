from spacy.lang.en import English

from ca.question_generator_syntactic.question import generate_questions


def spacy_sentencizer():
    nlp = English()  # just the language with no model
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)
    fs = open('../data/bldgpermit.txt')
    doc = nlp(fs.read())
    index = 0
    for sent in doc.sents:
        index = index + 1
        str = sent.text.replace('\n', ' ').replace('\t', ' ').strip()
        generate_questions(str)
    print(index)


if __name__ == "__main__":
    spacy_sentencizer()