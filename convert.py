import sys

def convert():
    with open('App.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out = []
    in_css = False
    for line in lines:
        if 'st.set_page_config' in line:
            continue
        if 'st.markdown' in line and '<style>' in line:
            in_css = True
            continue
        if 'unsafe_allow_html=True' in line and in_css:
            in_css = False  # Skip the ending line
            continue
        if '</style>' in line and 'unsafe_allow_html=True' in line:
            in_css = False
            continue
        if in_css:
            continue
            
        # Optional: remove the watermark UI rendering since Astor has its own or we can leave it
        if 'watermark_html =' in line:
            # We will just let it be, the CSS won't override Astor's
            pass
            
        # Get rid of standalone triple quotes if that was the end of a big block
        if line.strip() == '\"\"\", unsafe_allow_html=True)' and in_css:
            in_css = False
            continue
            
        out.append(line)

    final = [
        'import streamlit as st\n',
        'import pandas as pd\n',
        'import base64\n',
        'import os\n',
        'import plotly.express as px\n',
        'import io\n',
        'from PIL import Image\n\n',
        'def render_planificador():\n'
    ]
    
    for line in out:
        if line.startswith('import ') or line.startswith('from '): continue
        # Add 4 spaces of indentation
        # Replace empty lines with empty lines
        if line.strip() == '':
            final.append('\n')
        else:
            final.append('    ' + line)

    with open('planificador.py', 'w', encoding='utf-8') as f:
        f.writelines(final)

if __name__ == '__main__':
    convert()
