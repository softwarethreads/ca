import sys
import argparse
from question_generator import QuestionGenerator


def add_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sentence', type=str, help="The sentence for which questions are to be generated.")
    parser.add_argument('-t', '--question_type', type=str, default=['Wh', 'Are', 'Who', 'Do'], choices=['Wh', 'Are', 'Who', 'Do', 'All'], help='The types of questions to be generated.')
    return parser.parse_args()


def generate_questions(sentence):
    q = QuestionGenerator()
    question_list = q.generate_question(sentence, ['All'])
    for sent in question_list:
        qa = sent.split('\t')
        if (len(qa) >= 3):
            print("0  "+qa[0])
            print("1  "+qa[1])
            print("3  "+qa[3])
            print(" ")
