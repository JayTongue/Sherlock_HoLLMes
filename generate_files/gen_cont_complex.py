import random
import os
from itertools import zip_longest
from pathlib import Path
from pprint import pprint

from generate_txt import generate_files_to_count_main
from generate_clues import generate_clues_main
from conflict_checker import conflict_checker_main
from gen_different_filetypes import gen_different_filetypes_main

def gen_cont_complex_main(content_type, target_dir, count, problem_dist):
    generate_files_to_count_main(content_type, Path(target_dir), count)
    conflicts = True
    while conflicts:
        problems, used_names = generate_clues_main(problem_dist)
        conflicts = conflict_checker_main(used_names, target_dir)

    clues = interleaf_clues(problems)
    distribute_clues(clues, target_dir)

    for input_path in [Path(f'{target_dir}/{i}') for i in os.listdir(target_dir)]:
        with open(input_path, 'r') as infile:
            input_string = infile.read()
        os.remove(input_path)
        gen_different_filetypes_main(input_path, input_string)
    return problems

def interleaf_clues(problems):
    setup_clues = [] ; all_problems = []
    for problem_type in ['simple_retrieval', 'formal_logic', 'informal_logic']:
        all_problems.extend(problems[problem_type])

    all_setups = [problem['setup'] for problem in all_problems]

    for clues_at_position in zip_longest(*all_setups, fillvalue=None):
        for clue in clues_at_position:
            if clue is not None:
                setup_clues.append(clue)
    return setup_clues


def distribute_clues(clues, directory):
    directory = Path(directory)
    file_paths = sorted(directory.glob("*.txt"))
    
    clues = [f'\n    {i}    \n' for i in clues]
    if not file_paths:
        raise ValueError(f"No .txt files found in {directory}")
    
    num_files = len(file_paths) ; num_clues = len(clues)
    file_assignments = sorted([random.randint(0, num_files - 1) for _ in range(num_clues)])
    
    for clue, file_idx in zip(clues, file_assignments):
        filepath = file_paths[file_idx]
        
        with open(filepath, 'r') as f:
            content = f.read()

        inject_pos = random.randint(0, len(content))
        new_content = content[:inject_pos] + "\n" + clue + "\n" + content[inject_pos:]
        
        with open(filepath, 'w') as f:
            f.write(new_content)


if __name__ == '__main__':
    problems = gen_cont_complex_main('markov', 'data/outputs/test/', 5)
    pprint(problems)