
import sys

with open('Astor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Line numbers in view_file are 1-indexed.
    # Line 1591 is index 1590.
    # We want to indent from 1591 to 2466 (inclusive).
    # That is indices 1590 to 2465.
    if 1590 <= i <= 2465:
        new_lines.append('    ' + line)
    else:
        new_lines.append(line)

with open('Astor.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
