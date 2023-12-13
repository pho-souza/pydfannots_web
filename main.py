import streamlit as st
import app.cli as cli
import os, zipfile
import re
import shutil
from io import StringIO

def create_folder(folder_name = 'temp'):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)

st.markdown('''
   # PyDF Annotation Extractor
   
   - Esse site tem por objetivo extrair anotações de arquivos PDF
''')



arquivo = st.file_uploader(
    'Send your file here!',
    type=['pdf']
)

pdf_file_exist = False
arquivo_pdf = ''

if arquivo:
    match arquivo.type.split('/'):
        case _, 'pdf':
            pdf_file_exist = True
            create_folder()  
else:
    create_folder()
    pdf_file_exist = False
    st.error('Não há arquivo PDF.')

if pdf_file_exist and arquivo:
    with st.form(key='my_form'):
        arquivo_pdf = os.path.join('temp', arquivo.name)
        with open(arquivo_pdf, 'wb') as f:
            f.write(arquivo.getbuffer())
            f.close()
        argument_input = ['-i',arquivo_pdf]
        argument_number_of_annots = argument_input + ['--count-annotations']
        number_of_annots = cli.main(argument_number_of_annots)
        st.write(f'This file has {number_of_annots} annotations')
        number_columns = st.number_input('Number of columns:', min_value = 1, value='min', max_value=10)
        intersection_level = st.number_input('Intersection level between highlight and text:', min_value = 0.0, value=0.10, max_value=1.0, step = 0.05)
        tolerance_level = st.number_input('Tolerance interval for columns:', min_value = 0.0, value=0.10, max_value=1.0, step = 0.05)
        extract_imgs = st.checkbox('Extract images', value = True)
        extract_inks = st.checkbox('Extract ink', value = True)
        # export_file = st.button('Extract annotations')
        template = st.sidebar.selectbox(
            'How would you like to be contacted?',
            cli.main(['--list-templates'])
        )
        submit_form = st.form_submit_button("Export annotations")
    if submit_form:
        create_folder('export')
        folder_name = re.sub('[.][PDFpdf]+$', '', arquivo.name)
        export_folder = os.path.join('export', folder_name)
        print(export_folder)
        create_folder(export_folder)
        argument_export = argument_input + ['--columns', str(int(number_columns))] + ['--tol', str(float(tolerance_level))] + ['-il', str(float(intersection_level))] + ['--template', str(template)]
        if not extract_imgs:
            argument_export  = argument_export + ['--no-image']
        if not extract_inks:
            argument_export  = argument_export + ['--no-ink-annotation']
        argument_export = argument_export + ['-o', str(export_folder)]
        st.text(str(argument_export))
        print("Executar!")
        cli.main(argument_export)
        print("Export complete!")
        zip_name = os.path.join('export', folder_name)
        
        shutil.make_archive(zip_name, "zip", export_folder)
        with open(zip_name+'.zip', 'rb') as file:
            download_button = st.download_button(
                "Download file",
                data=file,
                file_name='annotations.zip')
        