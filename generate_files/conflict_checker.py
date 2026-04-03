import os
from pathlib import Path
import PyPDF2
from docx import Document
import striprtf.striprtf as striprtf


def conflict_checker_main(used_names: set, dir_path: str):
    conflicts = {}
    for used_name in used_names:
        results = check_conflicts(dir_path, used_name)
        if results:
            conflicts[used_name] = results
    return conflicts


def search_txt(filepath, search_string):
    """Search plain text files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return search_string.lower() in content.lower()
    except:
        return False

def search_pdf(filepath, search_string):
    """Search PDF files"""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if search_string.lower() in text.lower():
                    return True
        return False
    except:
        return False

def search_docx(filepath, search_string):
    """Search DOCX files"""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            if search_string.lower() in para.text.lower():
                return True
        return False
    except:
        return False

def search_rtf(filepath, search_string):
    """Search RTF files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            rtf_content = f.read()
            text = striprtf.rtf_to_text(rtf_content)
            return search_string.lower() in text.lower()
    except:
        return False

def check_conflicts(dir_path, search_string):
    """Search all supported files in directory"""
    results = []
    search_funcs = {
        '.txt': search_txt,
        '.pdf': search_pdf,
        '.docx': search_docx,
        '.rtf': search_rtf
    }
    
    all_files = []
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = Path(filepath).suffix.lower()
            if ext in search_funcs:
                all_files.append((filepath, ext))

    for filepath, ext in all_files:
        if search_funcs[ext](filepath, search_string):
            results.append(filepath)
            # print(f"Found in: {filepath}")
    
    return results