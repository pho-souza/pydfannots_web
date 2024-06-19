# -*- coding: utf-8 -*-
"""This module contain the NoteExtractor module

This module is used to extract annotations from PDF files.
"""

import os
import re
import shutil
from importlib import reload

import fitz

import app.utils as utils
from app.cfg import Config_file


class NoteExtractor:
    def __init__(self, file: str = ''):
        """
        Initalize the NoteExtractor class and initial variables.
        Args:
            file (str, optional): PDF file location. Defaults to ''.
        """
        self.add_pdf(file)
        self.add_config()
        self.__threshold_intersection = self.config[
            'INTERSECTION_LEVEL'
        ]  # if the intersection is large enough.
        self.__path_template = os.path.abspath(self.config['TEMPLATE_FOLDER'])
        self.highlights = list()
        self.metadata = None
        self.pages = list()

    def __exit__(self):
        """
        Close pdf file before close.
        """
        self.close()

    def add_pdf(self, file: str = '', filebyte = None):
        """
        Load PDF file.
        """
        if file == '':
            pass
        elif not os.path.exists(file):
            raise ValueError('This file does not exist.')
        elif os.path.isdir(file):
            raise ValueError('This path is a folder.')
        elif re.search('[.](pdf|PDF)', os.path.basename(file)) == None:
            print(file)
            raise ValueError('This is not a PDF file.')
        elif os.path.getsize(file) == 0:
            raise ValueError('Cannot open empty PDF.')

        if filebyte:
            self.file = filebyte
        else:
            self.file = file
        self.pdf = fitz.open(self.file)

    def notes_extract(self, intersection_level: float = 0.1):
        """
        Extract annotations from PDF file.

        The method will extract annotations from all the pages in PDF file and assign to highlight variable.
        The informations collected are: type, page, author, rect_coord, start_xy,
        text, conent, created, modified, color.

        Description of the variables:
            type: the type of annotation. The types are defined in PDF reference. The most common types are:
                - Highlight
                - Text
                - FreeText
                - Underline
                - Squared
                - Ink
                - Squiggly
            page: the page position in the PDF file (start from 1)
            author: the author of the annotation
            rect_coord: coordinates of the annotation. Defined as a list of 4 elements.
                The 1st is the x0 position. The 2nd is the y0 position. The 3rd and the 4th are the x1 and y1.
            start_xy: the x0, y0 coordinate.
            text: text notes taken by the user in the annotation.
            content: text extract from the annotation positions in the PDF file.
            created: date where annotation was created.
            modified: date where annotation was modified.
            color: color extract from annotation in RGB list.
        """
        if intersection_level > 1.0 or intersection_level < 0.0:
            raise ValueError(
                'Intersection level must be beteween 0.0 and 1.0.'
            )

        self.__threshold_intersection = intersection_level
        for page_num in self.list_pages:
            page = self.pdf[page_num]
            page_bound = list(page.bound())
            annotations = page.annot_xrefs()
            if annotations:
                words = page.get_text('words')
                for annot in page.annots():
                    # margin = (-2, -2, 2, 2)
                    anotacao = {}
                    anotacao['type'] = annot.type[1]
                    anotacao['page'] = page_num + 1
                    anotacao['author'] = annot.info['title']
                    anotacao['rect_coord'] = list(annot.rect)
                    # Adjust by page size
                    anotacao['rect_coord'][0] = (
                        anotacao['rect_coord'][0] / page_bound[2]
                    )
                    anotacao['rect_coord'][1] = (
                        anotacao['rect_coord'][1] / page_bound[3]
                    )
                    anotacao['rect_coord'][2] = (
                        anotacao['rect_coord'][2] / page_bound[2]
                    )
                    anotacao['rect_coord'][3] = (
                        anotacao['rect_coord'][3] / page_bound[3]
                    )
                    
                    # Check coord:
                   #  bigger_than_page = True
                    bigger_than_page = (
                        anotacao['rect_coord'][0] < 0.0 or
                        anotacao['rect_coord'][1] < 0.0 or
                        anotacao['rect_coord'][2] < 0.0 or
                        anotacao['rect_coord'][3] < 0.0 or
                        anotacao['rect_coord'][0] > 1.0 or
                        anotacao['rect_coord'][1] > 1.0 or
                        anotacao['rect_coord'][2] > 1.0 or
                        anotacao['rect_coord'][3] > 1.0
                    )
                    
                    if bigger_than_page:
                        continue

                    # print(annot.type[1])
                    anotacao['start_xy'] = anotacao['rect_coord'][0:2]
                    text = ''
                    if (
                        annot.vertices
                        and len(annot.vertices) >= 4
                        and not annot.type[1] in ['Ink', 'Freetext']
                    ):
                        text = self.__extract_annot(annot, words)
                        anotacao['text'] = text
                    anotacao['content'] = annot.info['content']
                    anotacao['created'] = annot.info['creationDate']
                    anotacao['modified'] = annot.info['modDate']
                    anotacao['has_img'] = False
                    anotacao['img_path'] = ''
                    if annot.colors['fill']:
                        anotacao['color'] = list(annot.colors['fill'])
                    elif annot.colors['stroke']:
                        anotacao['color'] = list(annot.colors['stroke'])
                    else:
                        anotacao['color'] = list((0, 0, 0))
                    self.highlights.append(anotacao)

            self.reorder_columns(columns=1)
            self.get_metadata()

    @property
    def count_highlights(self):
        annotation_counter = 0
        # self.pages = []
        for pages in self.pdf:
            annotations = pages.annot_xrefs()
            if annotations:
                for annot in pages.annots():
                    annotation_counter += 1
                # self.pages.append(pages)
        # print(f'There is {annotation_counter} annotations in this file.')
        return annotation_counter

    @property
    def list_pages(self):
        annotation_counter = 0
        pages = list()
        for page in self.pdf:
            annotations = page.annot_xrefs()
            if annotations:
                pages.append(page.number)
        self.pages = pages
        return pages
    
    @property
    def number_of_pages(self):
        return self.pdf.page_count

    def add_config(self, config=''):
        """Add configuration file

        Args:
            config (str): Path to json config file.
        """
        is_empty_file = config == ''

        if not is_empty_file:
            if not os.path.exists(config):
                raise ValueError(
                    f'The config file "{config}" file does not exist.'
                )
            elif os.path.isdir(config):
                raise ValueError(f'{config} path is a folder.')
            elif re.search('[.](json|JSON)', os.path.basename(config)) == None:
                raise ValueError(
                    f'The config file "{config}" is not a json file.'
                )
            elif os.path.getsize(config) == 0:
                raise ValueError(f'Cannot open "{config}". Empty document')

        self.config = Config_file(config).config

        utils.DEFAULT_COLOR = self.config['DEFAULT_COLOR']
        utils.PATH = self.config['TEMPLATE_FOLDER']
        utils.DEFAULT_TEMPLATE = self.config['DEFAULT_TEMPLATE']
        utils.DEFAULT_COLOR = self.config['DEFAULT_COLOR']

        reload(utils)

    def __check_contain(self, r_word, points):
        """If `r_word` is contained in the rectangular area.

        The area of the intersection should be large enough compared to the
        area of the given word.

        Args:
            r_word (fitz.Rect): rectangular area of a single word.
            points (list): list of points in the rectangular area of the
                given part of a highlight.

        Returns:
            bool: whether `r_word` is contained in the rectangular area.
        """
        # `r` is mutable, so everytime a new `r` should be initiated.
        r = fitz.Quad(points).rect
        r.intersect(r_word)

        if r.get_area() >= r_word.get_area() * (self.__threshold_intersection):
            contain = True
        else:
            contain = False
        return contain

    def __extract_annot(self, annot, words_on_page):
        """Extract words in a given highlight.

        Args:
            annot (fitz.Annot): [description]
            words_on_page (list): [description]

        Returns:
            str: words in the entire highlight.
        """
        quad_points = annot.vertices
        quad_count = int(len(quad_points) / 4)
        sentences = ['' for i in range(quad_count)]
        for i in range(quad_count):
            points = quad_points[i * 4 : i * 4 + 4]
            words = [
                w
                for w in words_on_page
                if self.__check_contain(r_word=fitz.Rect(w[:4]), points=points)
            ]
            sentences[i] = ' '.join(w[4] for w in words)
        sentence = ' '.join(sentences)

        return sentence

    def import_template(self, path: str):
        """
        Import a template file to template folder

        Args:
            path (str): path of the file
        """
        full_path = os.path.abspath(path)

        if os.path.exists(full_path) is False:
            raise ValueError('This file does not exist.')

        file_name = os.path.basename(full_path)

        move_path = self.__path_template + '/' + file_name

        move_path = os.path.abspath(move_path)

        if os.path.isfile(full_path):
            shutil.copy(src=full_path, dst=move_path)
            print('File {} imported into {}'.format(full_path, move_path))
        if os.path.isdir(full_path):
            shutil.copytree(src=full_path, dst=move_path)
            print('Folder {} imported into {}'.format(full_path, move_path))

    def rename_template(self, name: str, new_name: str):
        """
        Rename a template from templates folder.

        Args:
            name (str): actual template name
            new_name (str): New template name
        """
        # print(type(name))
        if name not in self.templates:
            raise ValueError('This template does not exist.')

        if name:
            actual_file = self.__path_template + '/' + name
            # actual_file = utils.path_normalizer(os.path.abspath(actual_file))
            actual_file = os.path.abspath(actual_file)
        if new_name:
            new_file = self.__path_template + '/' + new_name
            # new_file = utils.path_normalizer(os.path.abspath(new_file))
            new_file = os.path.abspath(new_file)
        if os.path.exists(actual_file):
            shutil.move(actual_file, new_file)
            print('File {} renamed to {}'.format(actual_file, new_file))

    def remove_template(self, name: str):
        """Remove template from template folder

        Args:
            name (str): Template to be removed
        """
        if name not in self.templates:
            raise ValueError('This template does not exist.')

        file = self.__path_template + '//' + name
        file = utils.path_normalizer(os.path.abspath(file))
        if os.path.exists(file):
            os.remove(file)
            print('File {} removed from templates folder'.format(file))

    @property
    def templates(self):
        """Return templates in tempaltes folder.

        Returns:
            list: list of files in template folder
        """
        path_template = self.__path_template
        files = os.listdir(path_template)
        # if isinstance(files, str):
        #     files = list(files)
        for file in files:
            full_path = os.path.join(path_template, file)
            if os.path.isdir(full_path):
                files.remove(file)
        return files

    def get_metadata(self):
        """
        Get the pdf metadata and assign to to self.metadata
        """
        self.metadata = self.pdf.metadata

    def adjust_date(self) -> str:
        """
        Converts the created date to the format YYYY-MM-DD HH:mm:ss
        """
        for annot in self.highlights:
            date_created = re.sub('D:', '', annot['created'])
            date_modified = re.sub('D:', '', annot['modified'])
            # Extract Date in format: YYYY-MM-DD HH:MM:SS
            regex_pattern_date = '([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2}).*'
            regex_export_date = r'\1-\2-\3 \4:\5:\6'
            date_created = re.sub(
                regex_pattern_date, regex_export_date, date_created
            )
            date_modified = re.sub(
                regex_pattern_date, regex_export_date, date_modified
            )
            annot['created'] = date_created
            annot['modified'] = date_modified

    def adjust_color(self):
        """
        Convert the RGB color to classified group. This method converts RGB to HSL and convert HSL to categorical
        color names. The default color is Yellow
        """
        for annot in self.highlights:
            color = annot['color']
            color_hls = utils.convert_to_hls(color)
            colors = utils.colors_names(color_hls)
            annot['color_name'] = colors

    def adjust_text(self):
        """
        Adjust text with hifenization and remove all the linebreaks from content.
        """
        for annot in self.highlights:
            text = annot['content']
            text = utils.cleanup_text(text)
            text = utils.merge_lines(captured_text=text, remove_hyphens=True)
            annot['content'] = text

    def extract_image(self, location: str, folder='img/'):
        """
        Extract the images from Square annotations and save as png files.

        Args:
            location: path location
        Folder:
            Folder created inside location to store images.
        """
        self.reload()
        if 'annot_number' not in locals():
            annot_number = 0
        for annot in self.highlights:
            if annot['type'] == 'Square':
                annot_number = annot_number + 1
                page_number = annot['page']
                page = page_number - 1

                pdf_page = self.pdf[page]

                # pdf_page.set_rotation(90)

                number_of_rotation = pdf_page.rotation

                pdf_page.set_rotation(0)

                # Remove annotations in the page
                for annotation in pdf_page.annots():
                    # print(annotation)
                    pdf_page.delete_annot(annotation)

                user_space = annot['rect_coord']
                # for user_space_index in range(0, 4):
                #     if user_space[user_space_index] < 0:
                #         user_space[user_space_index] = 0
                # area = pdf_page.get_pixmap(dpi = 300)
                page_size = pdf_page.bound()
                # area = area.derotation_matrix
                
                # print(page_size)
                area = fitz.Rect()

                area.x0 = user_space[0] * page_size.x1
                area.x1 = user_space[2] * page_size.x1
                area.y0 = user_space[1] * page_size.y1
                area.y1 = user_space[3] * page_size.y1


                clip = fitz.Rect(area.tl, area.br)
                
                if area.x0 == area.x1 or area.y0 == area.y1:
                    continue

                # clip.set_rotation(number_of_rotation)
                # print(clip)

                if not os.path.exists(location):
                    os.mkdir(location)
                if not os.path.exists(location + '/' + folder):
                    os.mkdir(location + '/' + folder)

                file = re.sub('(.*/|.*\\\\)', '', self.file)
                file = re.sub('[.]pdf', '', file)
                file = re.sub('[ -]+', '_', file)
                file = re.sub('[_]+', '_', file)
                file = utils.path_normalizer(file)
                page = page + 1

                file_name = (
                    file + '_p' + str(page) + '_' + str(annot_number) + '.png'
                )

                file_export = location + '/' + folder + '/' + file_name
                # print(file_export)

                file_export = utils.path_normalizer(
                    os.path.abspath(file_export)
                )

                img_folder = folder + '/' + file_name
                # img_folder = os.path.abspath(img_folder)
                img_folder = re.sub('/+', '/', img_folder)
                img_folder = utils.path_normalizer(img_folder)
                
                condition_size = clip.x0 >= 0.0 and clip.x1 >= 0.0 and clip.y0 >= 0.0 and clip.y1 >= 0.0
                condition_height = clip.y0 >= page_size.y0  and clip.y1 <= page_size.y1
                condition_width = clip.x0 >= page_size.x0  and clip.x1 <= page_size.x1
                
                # print(f'Condition size: {condition_size}')
                # print(f'Condition height: {condition_height}')
                # print(f'Condition width: {condition_width}')
                # print(f'clip: {clip}')
                # print(f'page_size: {page_size}')

                if condition_size and condition_height and condition_width:
                    # print(page_size)
                    img = pdf_page.get_pixmap(clip=clip, dpi=300)
                    img.save(file_export)

                if os.path.exists(file_export):
                    annot['has_img'] = True
                    annot['img_path'] = img_folder
                    if number_of_rotation > 0:
                        img_pil = Image.open(fp=file_export)
                        img_pil = img_pil.rotate(
                            -number_of_rotation, expand=True
                        )
                        img_pil.save(fp=file_export)
                        img_pil.close()
                else:
                    annot['has_img'] = False
                    annot['img_path'] = ''

            self.reload()

    def reorder_custom(
        self, criteria=['page', 'start_xy'], ascending: bool = True
    ):
        """
        Reorder the annotations using annotation structure variables.

        Args:
            criteria: list of variable names. The position in list define the order to be sorted.
            ascending: order to be used. If True, use the ascending order. If False, descending order.
        """
        self.highlights = utils.annots_reorder_custom(
            self.highlights, criteria=criteria, ascending=ascending
        )

    def reorder_columns(self, columns=1, tolerance=0.1):
        """
        Reorder the annotation using the y position of the element by number of columns.

        The default number of columns is 1. If the PDF has 2 or more columns,
        will divide the page in columns with same width, using a interval
        of tolerance defined in a interval from 0 to 1.

        The tolerance represent a page width percentage to be added to columns interval.
        If tolerance = 0, the columns limits will correspond to the exact division of 1/columns.
        If tolerance = 0.1, the columns will correspond to a interval between 1/columns-0.1 to 1/columns + 0.1.


        Args:
            columns: number of columns in the file
            tolerance: page width percentage to be considered in column size.


        """
        self.highlights = utils.annots_reorder_columns(
            self.highlights, columns=columns, tolerance=tolerance
        )

    def reload(self):
        """
        Close the PDF file and open the PDF file.
        """
        self.close()
        self.pdf = fitz.open(self.file)

    def extract_ink(self, location: str, folder='img/'):
        """
        Extract the ink annotations and save as png files.

        Args:
            location: path location
            folder: folder created inside location to store images.
        """
        list_pages = dict()
        if 'annot_number' not in locals():
            annot_number = 0
        for annot in self.highlights:
            if annot['type'] == 'Ink':
                if 'anterior_page' not in locals():
                    anterior_page = annot['page']
                    anterior_userspace = annot['rect_coord']
                    anterior = 1

                annot_number = annot_number + 1
                page_number = annot['page']
                page = page_number - 1

                pdf_page = self.pdf[page]

                # pdf_page.set_rotation(90)

                number_of_rotation = pdf_page.rotation

                pdf_page.set_rotation(0)

                # Remove annotations in the page
                try:
                    for annots in pdf_page.annots():
                        if annots.type[1] != 'Ink':
                            pdf_page.delete_annot(annots)
                except:
                    pass

                user_space = annot['rect_coord']
                # area = pdf_page.get_pixmap(dpi = 300)
                area = pdf_page.bound()
                page_area = pdf_page.bound()

                # if page_number == anterior_page:
                #     anterior += 1
                #     area.x0 = (
                #         min(user_space[0], anterior_userspace[0]) * area.x1
                #     )
                #     area.x1 = (
                #         max(user_space[2], anterior_userspace[2]) * area.x1
                #     )
                #     area.y0 = (
                #         min(user_space[1], anterior_userspace[1]) * area.y1
                #     )
                #     area.y1 = (
                #         max(user_space[3], anterior_userspace[3]) * area.y1
                #     )
                # else:
                #     anterior = 1
                area.x0 = user_space[0] * area.x1
                area.x1 = user_space[2] * area.x1
                area.y0 = user_space[1] * area.y1
                area.y1 = user_space[3] * area.y1

                clip = fitz.Rect(area.tl, area.br)
                page_numeration = 'p_' + str(page + 1)

                if not os.path.exists(location):
                    os.mkdir(location)
                if not os.path.exists(location + '/' + folder):
                    os.mkdir(location + '/' + folder)

                file = re.sub('(.*/|.*\\\\)', '', self.file)
                file = re.sub('[.]pdf', '', file)
                file = re.sub('[ -]+', '_', file)
                file = re.sub('[_]+', '_', file)
                file = utils.path_normalizer(file)
                page = page + 1

                file_name = (
                    file
                    + '_p'
                    + str(page)
                    + '_ink_'
                    + str(annot_number)
                    + '.png'
                )

                file_export = location + '/' + folder + '/' + file_name
                # print(file_export)

                file_export = utils.path_normalizer(
                    os.path.abspath(file_export)
                )

                img_folder = folder + '/' + file_name
                # img_folder = os.path.abspath(img_folder)
                img_folder = re.sub('/+', '/', img_folder)
                img_folder = utils.path_normalizer(img_folder)

                img = pdf_page.get_pixmap(clip=clip, dpi=300)
                # print(file_export)
                img.save(file_export)

                if os.path.exists(file_export):
                    annot['has_img'] = True
                    annot['img_path'] = img_folder
                    if number_of_rotation > 0:
                        img_pil = Image.open(fp=file_export)
                        img_pil = img_pil.rotate(
                            -number_of_rotation, expand=True
                        )
                        img_pil.save(fp=file_export)
                        img_pil.close()
                else:
                    annot['has_img'] = False
                    annot['img_path'] = ''

                # file_export = location + '/' + folder + '/' + file_name
                # # print(file_export)

                # file_export = location + '/' + folder + '/' + file_name
                # file_export = os.path.abspath(file_export)
                # file_export = utils.path_normalizer(file_export)
                # file_export = re.sub('/+', '/', file_export)

                # img_folder = folder + '/' + file_name
                # # img_folder = os.path.abspath(img_folder)
                # img_folder = utils.path_normalizer(img_folder)
                # img_folder = re.sub('/+', '/', img_folder)

                # list_pages[page_numeration] = {
                #     'page': page,
                #     'clip': clip,
                #     'file': file,
                #     'file_name': file_name,
                #     'file_export': file_export,
                # }

                # anterior_page = annot['page']
                # anterior_userspace = [
                #     clip.x0 / page_area[2],
                #     clip.y0 / page_area[3],
                #     clip.x1 / page_area[2],
                #     clip.y1 / page_area[3],
                # ]

        # # print(list_pages)
        # for pg in list_pages:
        #     if not os.path.exists(location):
        #         os.mkdir(location)
        #     if not os.path.exists(location + '/' + folder):
        #         os.mkdir(location + '/' + folder)

        #     pdf_page = self.pdf[list_pages[pg]['page']]

        #     img = pdf_page.get_pixmap(clip=list_pages[pg]['clip'], dpi=300)
        #     # print(file_export)
        #     # if anterior <= anterior_number:
        #     img.save(list_pages[pg]['file_export'])

        #     for annot in self.highlights:
        #         if os.path.exists(file_export):
        #             annot['has_img'] = True
        #             annot['img_path'] = img_folder
        #             if number_of_rotation > 0:
        #                 img_pil = Image.open(fp=file_export)
        #                 img_pil = img_pil.rotate(
        #                     -number_of_rotation, expand=True
        #                 )
        #                 img_pil.save(fp=file_export)
        #                 img_pil.close()
        #         else:
        #             annot['has_img'] = False
        #             annot['img_path'] = ''

        for annot in self.highlights[:]:
            if annot['type'] == 'Ink' and not 'has_img' in annot:
                # print(annot)
                self.highlights.remove(annot)
        self.reload()

    def close(self):
        """
        Close the PDF file.
        """
        self.pdf.close()
