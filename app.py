import streamlit as st
import app.cli as cli
import os, zipfile, tempfile
import re
import shutil
from io import StringIO

from streamlit_pdf_viewer import pdf_viewer
from streamlit_extras.stylable_container import stylable_container
import streamlit.components.v1 as components


custom_css_mk = """
<style>
img{
    max-width: 100%;
}
</style>
"""


def create_folder(folder_name = 'temp'):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name,ignore_errors=True)
        os.makedirs(folder_name, exist_ok=True)
    else:
        os.makedirs(folder_name, exist_ok=False)

def show_templates(folder = ''):
    files_dict = dict()
    if os.path.isdir(folder):
        list_files = os.listdir(folder)
        for i in list_files:
            file = os.path.join(folder, i)
            if os.path.isfile(file):
                files_dict[i] = i
    return files_dict

def load_html(folder, html):
    selected_file = os.path.join(folder, html)
    if re.search('[.]html', selected_file):
        HtmlFile = open(selected_file, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        source_code = re.sub('img/','app/static/img/',source_code)
        components.html(source_code,scrolling=True,
                        height=800)
    elif re.search('[.]md', selected_file):
        HtmlFile = open(selected_file, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        source_code = re.sub('img/','app/static/img/',source_code)
        source_code = custom_css_mk + source_code
        st.markdown(source_code, unsafe_allow_html=True)
    elif re.search('[.]json', selected_file):
        HtmlFile = open(selected_file, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        source_code = re.sub('img/','app/static/img/',source_code)
        st.json(source_code)

def load_pdf(folder, pdf_file):
    selected_file = os.path.join(folder, pdf_file)
    local_file = re.sub('\\\\','/',selected_file)
    if os.path.exists(selected_file):
        print('pdf localizado')
        pdf_viewer(input = local_file, width=1000)
    else:
        print('PDF NÃO LOCALIZADO')
        pdf_viewer(input = local_file, width=1000)


number_of_annots = 0
create_folder()


st.markdown('''
   # PyDF Annotation Extractor
   
   - Esse site tem por objetivo extrair anotações de arquivos PDF
   - Os resultados são baixados em um arquivo zipzado.
''')

type_of_export = st.sidebar.selectbox(
    'What type of extraction do you want?',
    ['template','json','csv']
)

if str(type_of_export) == 'template':
    template = st.sidebar.selectbox(
                    'Which template do you want to use?',
                    cli.main(['--list-templates'])
                )

tab_extract, tab_pdf_example, tab_templates, tab_example = st.tabs(['Extract', 'PDF_Test', 'Templates', 'Example'])

with tab_extract:
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
            if number_of_annots > 0:
                st.write(f'This file has {number_of_annots} annotations')
                number_columns = st.number_input('Number of columns:', min_value = 1, value='min', max_value=10)
                intersection_level = st.number_input('Intersection level between highlight and text:', min_value = 0.0, value=0.10, max_value=1.0, step = 0.05)
                tolerance_level = st.number_input('Tolerance interval for columns:', min_value = 0.0, value=0.10, max_value=1.0, step = 0.05)
                extract_imgs = st.checkbox('Extract images', value = True)
                extract_inks = st.checkbox('Extract ink', value = True)
                # export_file = st.button('Extract annotations')
                submit_form = st.form_submit_button("Export annotations")

        if number_of_annots > 0 and submit_form:
            create_folder('export')
            folder_name = re.sub('[.][PDFpdf]+$', '', arquivo.name)
            export_folder = os.path.join('export', folder_name)
            print(export_folder)
            create_folder(export_folder)
            if str(type_of_export) == "template":
                argument_export = argument_input + ['--columns', str(int(number_columns))] + ['--tol', str(float(tolerance_level))] + ['-il', str(float(intersection_level))] + ['--template', str(template)]
            else:
                argument_export = argument_input + ['--columns', str(int(number_columns))] + ['--tol', str(float(tolerance_level))] + ['-il', str(float(intersection_level))] + ['-f', str(type_of_export)]
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
        else:
            st.write(f'This file has {number_of_annots} annotations. Attach a PDF with highlights.')

with tab_pdf_example:
    st.markdown('''
    # PDF ilustrativo
    
    - O PDF abaixo é um exemplo
    ''')
    selected_file = os.path.join('test','sample.pdf')
    # with open(selected_file, 'rb') as fo:
    #     pdf_viewer(input = fo)
    load_pdf('test','sample.pdf')


with tab_example:
    create_folder("examples")
    st.markdown('''
    # Exemplos
    
    - Esse site tem por objetivo extrair anotações de arquivos PDF
    - Os resultados são baixados em um arquivo zipzado.
    ''')
    templates_folder = os.path.join('app','templates')
    files = os.listdir(templates_folder)
    st.markdown('''
    # Templates
    ''')
    example_file = os.path.join('test', 'sample.pdf')
    argument_input = ['-i',example_file]
    argument_number_of_annots = argument_input + ['--count-annotations']
    number_of_annots = cli.main(argument_number_of_annots)
    if number_of_annots > 0:
        st.write(f'This file has {number_of_annots} annotations')
        number_columns = st.number_input('Number of columns:', min_value = 1, value='min', max_value=10)
        intersection_level = st.number_input('Intersection level between highlight and text:', min_value = 0.0, value=0.10, max_value=1.0, step = 0.05)
        tolerance_level = st.number_input('Tolerance interval for columns:', min_value = 0.0, value=0.10, max_value=1.0, step = 0.05)
        extract_imgs = st.checkbox('Extract images', value = True)
        extract_inks = st.checkbox('Extract ink', value = True)
        export_folder = os.path.join('examples')
        # export_file = st.button('Extract annotations')
        if str(type_of_export) == "template":
            templates = show_templates(templates_folder)
            selected_file = os.path.join(templates_folder, templates[template])
            argument_export = argument_input + ['--columns', str(int(number_columns))] + ['--tol', str(float(tolerance_level))] + ['-il', str(float(intersection_level))] + ['--template', str(template)]
            argument_export = argument_export + ['-o', str(export_folder)]  
            cli.main(argument_export)
            if re.search('html',template):
                load_html('examples', 'sample.html')
            elif re.search('md',template):
                load_html('examples', 'sample.md')
        if str(type_of_export) == "json":
            argument_export = argument_input + ['--columns', str(int(number_columns))] +  ['--f','json'] + ['-o', str(export_folder)]
            cli.main(argument_export)
            load_html('examples', 'sample.json')

with tab_templates:
    if str(type_of_export) == "template":
        templates_folder = os.path.join('app','templates')
        files = os.listdir(templates_folder)
        st.markdown('''
        # Templates
        ''')
        templates = show_templates(templates_folder)
        selected_file = os.path.join(templates_folder, templates[template])
        print(files == template)
        if os.path.exists(selected_file):
            loaded_template = open(selected_file,'r',encoding='utf-8').read()
            st.code(body=loaded_template,language='jinja2',line_numbers=True)