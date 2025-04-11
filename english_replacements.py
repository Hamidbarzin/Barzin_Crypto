#!/usr/bin/env python3
import re

def replace_persian_terms(file_path):
    # Load translations from file
    translations = {}
    with open('english_translations.txt', 'r', encoding='utf-8') as trans_file:
        for line in trans_file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                persian, english = line.split('=', 1)
                translations[persian] = english

    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Apply translations
    for persian, english in translations.items():
        content = content.replace(f"'{persian}'", f"'{english}'")
        content = content.replace(f"\"{persian}\"", f"\"{english}\"")
        
        # For signal values in dictionary entries
        content = content.replace(f"'signal': '{persian}'", f"'signal': '{english}'")
        
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Persian terms have been replaced with English in {file_path}")

if __name__ == "__main__":
    replace_persian_terms('main.py')