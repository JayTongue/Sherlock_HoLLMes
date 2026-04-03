import random
import json
import re
from datetime import datetime, timedelta
from pprint import pprint


def generate_clues_main(clue_order):
    with open('clues.json', 'r') as infile:
        clues = json.load(infile)
    # print(json.dumps(clues, indent=4))

    used_names = set()
    problems = {}
    for clue_type in ('simple_retrieval', 'formal_logic', 'informal_logic'):
        problems[clue_type] = []
        for _ in range(clue_order[clue_type]):
            filled_clues, used_names = make_clues(clue_type, used_names, clues)
            problems[clue_type].append(filled_clues)
            # print(json.dumps(filled_clues, indent=4))
            # print('-------------')
    # print(json.dumps(problems, indent=2))
    # print(used_names)
    return problems, used_names


def recur_get_vars(in_obj, form_vars=set()):
    if isinstance(in_obj, dict):
        for val in in_obj.values():
            recur_get_vars(val, form_vars)
    elif isinstance(in_obj, list):
        for item in in_obj:
            recur_get_vars(item, form_vars)
    elif isinstance(in_obj, str):
        form_vars.update(set(re.findall(r'\{.*?\}', in_obj)))
    return form_vars

def random_date(start_year=1990, end_year=2001):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime('%B %d, %Y')

def pull_random(form_vars: set, used_names: set, check_path, clues) -> dict:
    fill_dict = {}
    for var in form_vars:
        conflict = True
        while conflict:
            if var == '{fact}':
                chosen = random.choice(clues['facts'])
            elif var == '{topic}':
                chosen = random.choice(clues['topics'])
            elif var == '{report}':
                chosen = random.choice(clues['reports'])
            elif var == '{date}':
                chosen = random_date()
            else:
                names = [name for name in clues['names'] if name not in used_names]
                rand_name = random.choice(names)
                chosen = rand_name
                used_names.add(rand_name)

            conflict = False
            fill_dict[var[1:-1]] = chosen
    return fill_dict, used_names


def make_clues(clue_type: str, used_names, clues):
    filled = {'setup': [], 'questions': []}
    rand_selection = clues['templates'][clue_type][random.randint(0, len(clues['templates'][clue_type])-1)]
    form_vars = recur_get_vars(rand_selection)
    fill_dict, used_names = pull_random(form_vars, used_names, 'data/outputs/markov', clues)
    for i in rand_selection['setup']:
        filled['setup'].append(i.format_map(fill_dict))
    for k in rand_selection['questions']:
        filled['questions'].append({'ques': k['ques'].format_map(fill_dict), 
                       'ans': k['ans'].format_map(fill_dict)})
    return filled, used_names

if __name__ == '__main__':
    problems, used_names = generate_clues_main({'simple_retrieval': 1, 'formal_logic': 2, 'informal_logic': 3})
    pprint(problems)