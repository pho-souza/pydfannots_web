import os
import re
import shutil
import tempfile
import zipfile
from io import StringIO

import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.stylable_container import stylable_container
from streamlit_pdf_viewer import pdf_viewer

import app.cli as cli
import languages as lang

CUSTOM_CSS_MK = """
<style>
img{
    max-width: 100%;
}
</style>
"""

DEFAULT_LANGUAGE = "en"
TEXTS = lang.texts


def create_folder(folder_name="temp"):
    """create_folder creates new folders in the project and remove the old folders.

    Args:
        folder_name (str, optional): _description_. Defaults to "temp".
    """
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name, ignore_errors=True)
        os.makedirs(folder_name, exist_ok=True)
    else:
        os.makedirs(folder_name, exist_ok=False)


def show_templates(folder=""):
    """show_templates gets the templates inside a folder

    Args:
        folder (str, optional): _description_. Defaults to "".

    Returns:
        _type_: _description_
    """
    files_dict = dict()
    if os.path.isdir(folder):
        list_files = os.listdir(folder)
        for i in list_files:
            file = os.path.join(folder, i)
            if os.path.isfile(file):
                files_dict[i] = i
    return files_dict


def load_html(folder, html):
    """load_html loads a page inside page. It can be a html file, an Markdown file or a json file.

    Args:
        folder (_type_): folder location
        html (_type_): name of html file
    """
    selected_file = os.path.join(folder, html)
    if re.search("[.]html", selected_file):
        html_file = open(selected_file, "r", encoding="utf-8")
        source_code = html_file.read()
        source_code = re.sub("img/", "app/static/img/", source_code)
        components.html(source_code, scrolling=True, height=800)
    elif re.search("[.]md", selected_file):
        html_file = open(selected_file, "r", encoding="utf-8")
        source_code = html_file.read()
        source_code = re.sub("img/", "app/static/img/", source_code)
        source_code = CUSTOM_CSS_MK + source_code
        st.markdown(source_code, unsafe_allow_html=True)
    elif re.search("[.]json", selected_file):
        html_file = open(selected_file, "r", encoding="utf-8")
        source_code = html_file.read()
        source_code = re.sub("img/", "app/static/img/", source_code)
        st.json(source_code)


def load_pdf(folder, pdf_file):
    """load_pdf will insert the pdf_file in the page

    Args:
        folder (_type_): string
        pdf_file (_type_): _description_
    """
    local_file = os.path.join(folder, pdf_file)
    if os.path.exists(local_file):
        print("pdf localizado")
        pdf_viewer(input=local_file, width=1000)
    else:
        print("PDF NÃO LOCALIZADO")
        # pdf_viewer(input = local_file, width=1000)


NUMBER_OF_ANNOTS = {}
create_folder()

language_select = st.sidebar.selectbox(
    TEXTS["sidebarLanguageChoose"][DEFAULT_LANGUAGE], lang.languages
)

DEFAULT_LANGUAGE = lang.languages[language_select]


# Explicação página inicial
st.markdown(TEXTS["Homepage"][DEFAULT_LANGUAGE])


type_of_export = st.sidebar.selectbox(
    TEXTS["sidebarTemplateText"][DEFAULT_LANGUAGE], ["template", "json", "csv"]
)

if str(type_of_export) == "template":
    template = st.sidebar.selectbox(
        TEXTS["sidebarTemplateChoose"][DEFAULT_LANGUAGE], cli.main(["--list-templates"])
    )

tab_extract, tab_pdf_example, tab_templates, tab_example = st.tabs(
    [
        TEXTS["tabExtract"][DEFAULT_LANGUAGE], 
        TEXTS["tabPDFtest"][DEFAULT_LANGUAGE],
        TEXTS["tabTemplate"][DEFAULT_LANGUAGE],
        TEXTS["tabExample"][DEFAULT_LANGUAGE]
    ]
)

with tab_extract:
    file_list = []
    arquivo = st.file_uploader(TEXTS["btnSendFile"][DEFAULT_LANGUAGE], type=["pdf"],accept_multiple_files=True)
    # create_folder("export")
    pdf_file_exist = False
    arquivo_pdf = ""
    any_pdf_has_annot = False

    if arquivo:
        match arquivo[0].type.split("/"):
            case _, "pdf":
                pdf_file_exist = True
                create_folder()
    else:
        create_folder()
        pdf_file_exist = False
        st.error("Não há arquivo PDF.")

    for arq in arquivo:
        if arq is not None:
            file_list.append(arq)

    if pdf_file_exist and file_list:
        for arq in file_list:
            arquivo_pdf = os.path.join("temp", arq.name)
            with open(arquivo_pdf, "wb") as f:
                f.write(arq.getbuffer())
                f.close()
            argument_input = ["-i", arquivo_pdf]
            argument_NUMBER_OF_ANNOTS = argument_input + ["--count-annotations"]
            NUMBER_OF_ANNOTS[arq.name] = cli.main(argument_NUMBER_OF_ANNOTS)
            if NUMBER_OF_ANNOTS[arq.name] > 0:
                any_pdf_has_annot = True
            st.write(f"{arquivo_pdf} has {NUMBER_OF_ANNOTS[arq.name]} annotations")

        if any_pdf_has_annot:
            with st.form(key="my_form"):
                number_columns = st.number_input(
                    "Number of columns:", min_value=1, value="min", max_value=10
                )
                intersection_level = st.number_input(
                    "Intersection level between highlight and text:",
                    min_value=0.0,
                    value=0.10,
                    max_value=1.0,
                    step=0.05,
                )
                tolerance_level = st.number_input(
                    "Tolerance interval for columns:",
                    min_value=0.0,
                    value=0.10,
                    max_value=1.0,
                    step=0.05,
                )
                extract_imgs = st.checkbox("Extract images", value=True)
                extract_inks = st.checkbox("Extract ink", value=True)
                # export_file = st.button('Extract annotations')
                submit_form = st.form_submit_button("Export annotations")
            if submit_form:
                # print(export_folder)
                # create_folder(export_folder)
                if str(type_of_export) == "template":
                    argument_export = (
                        ["--columns", str(int(number_columns))]
                        + ["--tol", str(float(tolerance_level))]
                        + ["-il", str(float(intersection_level))]
                        + ["--template", str(template)]
                    )
                else:
                    argument_export = (
                        ["--columns", str(int(number_columns))]
                        + ["--tol", str(float(tolerance_level))]
                        + ["-il", str(float(intersection_level))]
                        + ["-f", str(type_of_export)]
                    )
                if not extract_imgs:
                    argument_export = argument_export + ["--no-image"]
                if not extract_inks:
                    argument_export = argument_export + ["--no-ink-annotation"]

                for arq in file_list:
                    arquivo_pdf = os.path.join("temp", arq.name)
                    if NUMBER_OF_ANNOTS[arq.name] > 0:
                        print(arquivo_pdf)
                        argument_input = ["-i", arquivo_pdf]
                        folder_name = re.sub("[.][PDFpdf]+$", "", arq.name)
                        export_folder = os.path.join("export")
                        argument_export_final = argument_input + argument_export + ["-o", str(export_folder)]
                        st.text(str(argument_export_final))
                        print(argument_export_final)
                        cli.main(argument_export_final)
                        print("Export complete!")
                zip_name = os.path.join("export")

                shutil.make_archive(zip_name, "zip", export_folder)
                with open(zip_name + ".zip", "rb") as file:
                    download_button = st.download_button(
                        "Download file", data=file, file_name="annotations.zip"
                    )
            else:
                st.write(
                    f"This file has {NUMBER_OF_ANNOTS} annotations. Attach a PDF with highlights."
                )

with tab_pdf_example:
    st.markdown(
        """
    # PDF ilustrativo
    
    - O PDF abaixo é um exemplo
    """
    )
    selected_file = os.path.join("test", "sample.pdf")
    # with open(selected_file, 'rb') as fo:
    #     pdf_viewer(input = fo)
    load_pdf("test", "sample.pdf")


with tab_example:
    create_folder("examples")
    st.markdown(
        TEXTS["textExample"][DEFAULT_LANGUAGE]
    )
    templates_folder = os.path.join("app", "templates")
    files = os.listdir(templates_folder)
    st.markdown(
        """
    # Templates
    """
    )
    example_file = os.path.join("test", "sample.pdf")
    argument_input = ["-i", example_file]
    argument_NUMBER_OF_ANNOTS = argument_input + ["--count-annotations"]
    NUMBER_OF_ANNOTS = cli.main(argument_NUMBER_OF_ANNOTS)
    if NUMBER_OF_ANNOTS > 0:
        st.write(f"This file has {NUMBER_OF_ANNOTS} annotations")
        number_columns = st.number_input(
            "Number of columns:", min_value=1, value="min", max_value=10
        )
        intersection_level = st.number_input(
            "Intersection level between highlight and text:",
            min_value=0.0,
            value=0.10,
            max_value=1.0,
            step=0.05,
        )
        tolerance_level = st.number_input(
            "Tolerance interval for columns:",
            min_value=0.0,
            value=0.10,
            max_value=1.0,
            step=0.05,
        )
        extract_imgs = st.checkbox("Extract images", value=True)
        extract_inks = st.checkbox("Extract ink", value=True)
        export_folder = os.path.join("examples")
        # export_file = st.button('Extract annotations')
        if str(type_of_export) == "template":
            templates = show_templates(templates_folder)
            selected_file = os.path.join(templates_folder, templates[template])
            argument_export = (
                argument_input
                + ["--columns", str(int(number_columns))]
                + ["--tol", str(float(tolerance_level))]
                + ["-il", str(float(intersection_level))]
                + ["--template", str(template)]
            )
            argument_export = argument_export + ["-o", str(export_folder)]
            cli.main(argument_export)
            if re.search("html", template):
                load_html("examples", "sample.html")
            elif re.search("md", template):
                load_html("examples", "sample.md")
        if str(type_of_export) == "json":
            argument_export = (
                argument_input
                + ["--columns", str(int(number_columns))]
                + ["--f", "json"]
                + ["-o", str(export_folder)]
            )
            cli.main(argument_export)
            load_html("examples", "sample.json")

with tab_templates:
    if str(type_of_export) == "template":
        templates_folder = os.path.join("app", "templates")
        files = os.listdir(templates_folder)
        st.markdown(
            """
        # Templates
        """
        )
        templates = show_templates(templates_folder)
        selected_file = os.path.join(templates_folder, templates[template])
        print(files == template)
        if os.path.exists(selected_file):
            loaded_template = open(selected_file, "r", encoding="utf-8").read()
            st.code(body=loaded_template, language="jinja2", line_numbers=True)
