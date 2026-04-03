'''
Helper for expediently copying into LLM chats
'''
import json
import sys
from random import randint

trial_num = sys.argv[2] ; trial_size = sys.argv[1]

filepath = f'data/sized/{trial_size}/{trial_num}/key_{trial_size}_{trial_num}.json'
with open(filepath, 'r') as infile:
    clues = json.load(infile)
question_battery = {}
for filetype in clues:
    questions, answers = [], []
    for qtype in clues[filetype]:
        for i in clues[filetype][qtype]:
            # print(i.keys())
            pick = randint(0, len(i['questions'])-1)
            questions.append(i['questions'][pick]['ques']) ; answers.append(i['questions'][pick]['ans'])
    questions.append('Answer all questions but DO NOT do a document by document analysis for ANY part of the response. DO NOT make a timeline.')

    question_battery[filetype] = {'questions': questions, 'answers': answers}
# print(json.dumps(question_battery, indent=0))

print(f'--------------- Size: {trial_size} | Trial: {trial_num} ---------------')
for ftype in ('contracts', 'enron', 'markov', 'random', 'zeros'):
    print(f'--------------- {ftype} {trial_size} | {trial_num} ---------------')
    print('--- questions ---')
    for h in question_battery[ftype]['questions']:
        print(h)
    print('--------------- answers ---------------')
    for j in question_battery[ftype]['answers']:
        print(j)