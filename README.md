# Sherlock HoLLMes
### An analysis of legal LLM retrieval abilities
#### Justin Tung, Reference Librarian and Lecturer, University of Texas School of Law

-------------------------------

This repo is sorted into 6 main directories:

* `./writeup/`
    * `writeup.md` - The final writeup and analysis
* `./analysis/`
    * `analyze_data.ipynb` - Analyzes the collected data for models and visualizations
    * `filesize_analysis.ipynb` - Analysis of Contracts and Enron corpora
* `./data/`
    * data files (uncommitted due to size)
* `./data_visualizations/`
    * exhibits for the writeup
* `./generate_files/`
    * `aggregated_run.ipynb` - The notebook that runs the other .py files to generate files
    * `conflict_checker.py` - Checks for conflicts between the underlying corpora and a selected name
    * `gen_cont_complex.py` - generates a file set of a given corpus at a given dir.
    * `gen_different_filetypes.py` - writes a given string to a random file type
    * `generate_clues.py` - Generate clues from the given template
    * `generate_txt.py` - Generate strings of a given corpora, of a given number, at a given path
* `./query_tools/`
    * `clues.json` - Clue templates
    * `query_builder.py` - simple script to make querying easier  
    * `results.json` - Recorded data from experimental trials