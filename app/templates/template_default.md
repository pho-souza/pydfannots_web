<<<<<<< HEAD:app/templates/template_default.md
# {{title}}

{% macro color_type(color) %}
{%- if color == "Green" %}

> [!question]
{%- elif color == 'Orange' %}

> [!example]
{%- elif color == 'Red' %}

> [!atencao]
{%- endif -%}
{% endmacro %}

{% set anterior = namespace('') %}
{% set anterior.content = highlights[0].content %}
{%- for annot  in highlights %}
{% if annot.type == 'Square' %}
{% if annot.has_img %}
![]({{annot.img_path}})
{% endif %}
{% elif annot.color_name == 'Cyan' %}

{% if annot.content.upper() == "#H1" or annot.content.upper() == "H1" %}
# {{annot.text}}

{% elif annot.content.upper() == "#H2" or annot.content.upper() == "H2" %}
## {{annot.text}}

{% elif annot.content.upper() == "#H3" or annot.content.upper() == "H3" %}
### {{annot.text}}

{% else %}
# {{annot.text}}

{% endif %}
{% elif annot.color_name == 'Yellow' %}
{% if annot.content == '-' %}
{{"- " ~ annot.text ~ "\n" }}
{%- elif annot.content == '+' and anterior.content == '+' -%}
{{- " " ~ annot.text ~ " " -}}
{%- elif anterior.content == '+' -%}
{% if annot.content and annot.content != "+" %}
{{- "> " ~ annot.text}}
- {{"> - " ~ annot.content}}
{% else %}
{{- " " ~ annot.text}}
{% endif %}
{% elif annot.content == '+' -%}
{{annot.text}} 
{%- elif annot.content %}

{{annot.text}}
- {{annot.content}}

{% else %}

{{annot.text}}

{% endif %}
{# Casos de callout #}
{% else %}
{%- if annot.content == '+' and anterior.content == '+' -%}
{{- " " ~ annot.text ~ " " -}}
{%- elif anterior.content == '+' -%}
{% if annot.content and annot.content != "+" %}
{{- " " ~ annot.text}}
> - - -
{{"> - " ~ annot.content}}
{% else %}
{{- " " ~ annot.text}}
{% endif %}
{% elif annot.content == '+' -%}
{{color_type(annot.color_name)}}
> {{annot.text}} 

{%- elif annot.content %}
{{color_type(annot.color_name)}}
> {{annot.text}}
> - - -
> {{annot.content}}

{% else %}
{{color_type(annot.color_name)}}
> {{annot.text}}


{% endif %}
{% endif %}
{%- if annot.content %}
{%- set anterior.content = annot.content -%}
{%- else -%}
{%- set anterior.content = '' -%}
{% endif -%}
{% endfor -%}

=======
# {{title}}

{% macro color_type(color) %}
{%- if color == "Green" %}


> [!question]
{%- elif color == 'Orange' %}


> [!example]
{%- elif color == 'Red' %}


> [!atencao]
{%- endif -%}
{% endmacro %}

{% set anterior = namespace('') %}
{% set anterior.content = highlights[0].content %}
{%- for annot  in highlights %}
{% if annot.type == 'Square' %}

{% if annot.has_img %}
![]({{annot.img_path}})

{% endif %}
{% elif annot.color_name == 'Cyan' %}

{% if annot.content == "#h1" or annot.content == "#H1" or  annot.content == "H1"%}
# {{annot.text}}

{% elif annot.content == "#h2" or annot.content == "#H2" or  annot.content == "H2" %}
## {{annot.text}}

{% elif annot.content == "#h2" or annot.content == "#H2" or  annot.content == "H2" %}
### {{annot.text}}

{% elif annot.content == "lembrar" %}
> [!Pesquisar]
> {{annot.text}}

{% else %}
# {{annot.text}}

{% endif %}
{% elif annot.color_name == 'Yellow' %}
{% if annot.content == '-' %}
{{"- " ~ annot.text ~ "\n" }}

{%- elif annot.content == '+' and anterior.content == '+' -%}
{{- " " ~ annot.text ~ " " -}}
{%- elif anterior.content == '+' -%}
{% if annot.content and annot.content != "+" %}
{{- "> " ~ annot.text}}
- {{"> - " ~ annot.content}}
{% else %}
{{- " " ~ annot.text}}
{% endif %}
{% elif annot.content == '+' -%}

{{annot.text}} 
{%- elif annot.content %}

{{annot.text}}
- {{annot.content}}

{% else %}

{{annot.text}}

{% endif %}
{# Casos de callout #}
{% else %}
{%- if annot.content == '+' and anterior.content == '+' -%}
{{- " " ~ annot.text ~ " " -}}
{%- elif anterior.content == '+' -%}
{% if annot.content and annot.content != "+" %}
{{- " " ~ annot.text}}
> - - -
{{"> - " ~ annot.content}}
{% else %}
{{- " " ~ annot.text}}
{% endif %}
{% elif annot.content == '+' -%}
{{color_type(annot.color_name)}}
> {{annot.text}} 

{%- elif annot.content %}
{{color_type(annot.color_name)}}
> {{annot.text}}
> - - -
> {{annot.content}}

{% else %}
{{color_type(annot.color_name)}}
> {{annot.text}}


{% endif %}
{% endif %}
{%- if annot.content %}
{%- set anterior.content = annot.content -%}
{%- else -%}
{%- set anterior.content = '' -%}
{% endif -%}
{% endfor -%}
>>>>>>> main:PyDFannots/templates/template_default.md
