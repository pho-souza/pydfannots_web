This project is a web version of [PyDFannots](https://github.com/pho-souza/PyDFannots/).

# Pre-requisites

This app uses PyMuPDF and Jinja2 to extract notes and highlights from PDF files.

For the web interface, it uses Streamlit library.

To install the required packages in python, uses:

```base
pip install -r requirements.txt
```

# How to use

There are two forms of execute PyDFannots Web:

```base
streamlit run app.py
```

Or 

```base
python -m streamlit run app.py
```

The app will open a page in your browser.

![Home page of your path.](imgs/pydf_annots_home_page.png)

After upload your PDF files in the defined area, you can set the extraction method (template, json or csv).

If you choose template, you'll have to choose a template. By default, there are 4 templates:
- HTML_DEFAULT.html
- HTML_DEFAULT_pt_BR.html
- MARKDOWN_DEFAULT.html
- MARKDOWN_DEFAULT_pt_BR.html

The tab **Example** shows you how the notes and highlights in **PDF example** tab will look after the extraction.

You can create new templates using [jinja2](https://jinja.palletsprojects.com/en/3.1.x/) and put them in the folder:

> app/templates

# Templates

## How to make templates?

PyDFannots uses the [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/templates/). Jinja2 is a templating language.

You can create basic templates basic using the following structure:

```jinja2
{% for annotation in highlights %}
...actions...
{% endfor %}
```

It can access the highlight using **dot** notation. The list of variables in each highlight is listed in [annotation structure](https://github.com/pho-souza/PyDFannots/blob/main/doc/Annotation_Structure.md) in PyDFannots Repo.

The following example uses ``annotation`` as the current annotation in the loop. ``text`` is one field of annotation.  

```jinja2
{% for annotation in highlights %}
{{annotation.text}}
{% endfor %}
```

You can access all the fields this way:

```jinja2
{% for annotation in annotations %}
{{annotation.content}}
{{annotation.text}}
{{annotation.page}}
...etc...
{% endfor %}
```


