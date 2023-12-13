"""
This File contains project functions
"""
import colorsys
import operator
import os
import pathlib
import re

from jinja2 import Environment, FileSystemLoader

from app.cfg import Config_file

CHARACTER_SUBSTITUTIONS = {
    'ﬀ': 'ff',
    'ﬁ': 'fi',
    'ﬂ': 'fl',
    'ﬃ': 'ffi',
    'ﬄ': 'ffl',
    '‘': "'",
    '’': "'",
    '“': '"',
    '”': '"',
    '…': '...',
}

config_file = os.path.abspath(pathlib.Path(__file__).parent) + (
    '/default_cfg.json'
)


def load_config_file(config_file=config_file):
    config_file = os.path.abspath(config_file)
    if os.path.exists(config_file):
        try:
            CONF = Config_file().load_cfg(config_file)
        except:
            CONF = Config_file()
    else:
        CONF = Config_file()
    return CONF


CONF = load_config_file()

if not 'DEFAULT_COLOR' in globals() or not 'DEFAULT_COLOR' in locals():
    # print("Assign globals")
    DEFAULT_COLOR = CONF.get_cfg('DEFAULT_COLOR')
    PATH = CONF.get_cfg('TEMPLATE_FOLDER')
    DEFAULT_TEMPLATE = CONF.get_cfg('DEFAULT_TEMPLATE')


TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.abspath(PATH)),
    trim_blocks=True,
    lstrip_blocks=False,
)


def cleanup_text(text: str) -> str:
    """
    Normalise line endings and replace common special characters with plain ASCII equivalents.
    Args:
        text: String to be cleaned.
    Return:
        str
    Examples:
        >>> cleanup_text('Somebody once told\\r-me the world is gonna roll-me')
        'Somebody once told\\n-me the world is gonna roll-me'
    """
    if '\r\n' in text:
        text = text.replace('\r\n', '\n')
    if '\r' in text:
        text = text.replace('\r', '\n')
    return ''.join([CHARACTER_SUBSTITUTIONS.get(c, c) for c in text])


def merge_lines(
    captured_text: str, remove_hyphens: bool = False, strip_space: bool = True
) -> str:
    """
    Merge and cleanup lines in captured text,  optionally removing hyphens.

    Any number of consecutive newlines is replaced by a single space,  unless the
    prior line ends in a hyphen,  in which case they are just removed entirely.
    This makes it easier for the renderer to "broadcast" newlines to active
    annotations regardless of box hits. (Detecting paragraph breaks is tricky,
    and left for future work!)
    Args:
        captured_text: String to be cleaned. str.
        remove_hyphens: Remove hyphens from linebreaks. bool
        strip_space: separe spaces from captured-text. bool
    Return:
        str
    Examples:
        >>> merge_lines(f"Somebody once told-\\n-me the world is gonna roll-me and this is beau-\\ntiful", remove_hyphens = True)
        'Somebody once told-me the world is gonna roll-me and this is beautiful'
    """
    results = []

    lines = captured_text.splitlines()
    for i in range(len(lines)):
        thisline = lines[i]
        if thisline == '':
            continue

        nextline = lines[i + 1] if i + 1 < len(lines) else None

        if (
            len(thisline) >= 2
            and thisline[-1] == '-'  # Line ends in an apparent hyphen
            and thisline[-2].islower()
        ):  # Prior character was a lowercase letter
            # We have a likely hyphen. Remove it if desired.
            if remove_hyphens:
                thisline = thisline[:-1]
        elif (
            not thisline[-1].isspace()
            and nextline is not None
            and (nextline == '' or not nextline[0].isspace())
        ):
            # Insert space to replace the line break
            thisline += ' '

        results.append(cleanup_text(thisline))

    if results and strip_space:
        results[0] = results[0].lstrip()
        results[-1] = results[-1].rstrip()

    return ''.join(results)


def convert_to_hls(colors: list) -> tuple:
    """
    Convert rgb colors to hsl color pattern

    """
    # print(isinstance(colors,  list))
    if isinstance(colors, list) and len(colors) == 3:
        (r, g, b) = colors
    else:
        (r, g, b) = DEFAULT_COLOR
    (h, l, s) = colorsys.rgb_to_hls(r, g, b)
    return (h, s, l)


def colors_names(colors_hls: tuple) -> str:
    """
    The colors name intervals are from mgmeyers: https://github.com/mgmeyers/pdfannots2json
    """
    if len(colors_hls) != 3:
        return 'none'
    else:
        (h, s, l) = colors_hls
        if l < 0.15:
            return 'Black'
        if l > 0.95:
            return 'White'
        if s < 0.2:
            return 'Gray'
        if h < 15 / 360:
            return 'Red'
        if h < 45 / 360:
            return 'Orange'
        if h < 65 / 360:
            return 'Yellow'
        if h < 160 / 360:
            return 'Green'
        if h < 190 / 360:
            return 'Cyan'
        if h < 265 / 360:
            return 'Blue'
        if h < 355 / 360 and l <= 0.35:
            return 'Purple'
        if h < 355 / 360:
            return 'Magenta'
        return 'Red'


def annots_reorder_custom(annotations, criteria=None, ascending=True) -> dict:
    """
    This function reordenate the annotations based on criteria order
    """
    # criteria = criteria
    validate_criteria = ['page', 'type', 'start_xy', 'author', 'created']
    for i in criteria:
        if i not in validate_criteria:
            print(
                i,
                ' criteria is not valid! Please use: ',
                str(validate_criteria),
            )
            print(criteria)
            return annotations

    # if isinstance(ordenation, list) and len(ordenation) != len(criteria):
    #     print("Ordenation not valid! Please use a list of" + len(criteria) + " strings,  or a simple string.")
    #     return annotations

    temp = annotations.copy()

    if ascending:
        temp = sorted(temp, key=operator.itemgetter(*criteria))
    else:
        temp = sorted(temp, key=operator.itemgetter(*criteria), reverse=True)

    return temp


def annots_reorder_columns(
    annotations: dict, columns=1, tolerance=0.1
) -> dict:
    """
    This function reordenate the annotations based on: page,  columns and vertical position
    """
    temp = []
    # temp2 = []

    # Columns size
    columns_x = []
    for i in range(0, columns + 1):
        col_widget = (1 / columns) * i
        columns_x.append(col_widget)

    # Get all values
    pages = []
    rect_coord = []
    index = []
    index_init = 0
    for annotation in annotations:
        index.append(index_init)
        pages.append(annotation['page'])
        rect_coord.append(annotation['rect_coord'])
        index_init = index_init + 1
        annotation['index'] = index_init

    pages = set(pages)
    annotation_index_x0 = [-1]
    annotation_index_x1 = [-1]
    # for page in pages:
    #     page_init = len(temp)
    for column in range(1, len(columns_x)):
        for annotation in annotations:
            # if  index not in annotation_index:
            index = annotation['index']
            x0 = annotation['rect_coord'][0]
            x1 = annotation['rect_coord'][2]
            y0 = annotation['rect_coord'][1]
            y1 = annotation['rect_coord'][3]
            annotation['y'] = y0
            column_min = columns_x[column - 1] - tolerance
            column_max = columns_x[column] + tolerance
            # print("\n\n\nColumn: ", column, "\n Min: ", column_min, "\nMax: ", column_max)
            if (
                x0 >= column_min
                and x0 < column_max
                and index not in annotation_index_x0
            ):
                annotation['column'] = [column]
                annotation_index_x0.append(index)
            if (
                x1 >= column_min
                and x1 < column_max
                and index not in annotation_index_x1
            ):
                annotation['column'].append(column)
                annotation_index_x1.append(index)

    for annotation in annotations:
        if annotation['column'][0] == annotation['column'][1]:
            annotation['column'] = annotation['column'][0]
        elif annotation['column'][0] == 1:
            annotation['column'] = 1.0
        else:
            annotation['column'] = max(annotation['column'])

    temp = annotations.copy()

    temp = sorted(temp, key=operator.itemgetter('page', 'column', 'y'))

    return temp


def path_normalizer(path: str):
    """
    Convert paths with \\ to /

    Args:
        path (str): string
    """
    result = re.sub('\\\\', '/', path)
    return result


def is_dir(path=''):
    return os.path.isdir(path)


def md_export(annotations, title='Title', template=DEFAULT_TEMPLATE):
    """
    Export the annotation using some jinja template.
    """
    # print(PATH)
    print(f'LEN HIGHLIGHTS: {len(annotations)}')

    md_template = TEMPLATE_ENVIRONMENT.get_template(template)
    retorno = md_template.render(title=title, highlights=annotations)

    return retorno
