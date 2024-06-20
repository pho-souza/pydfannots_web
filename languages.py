"""
Language settings
"""


languages = {
    'English': 'en',
    'Portuguese': 'pt_br'#,
    # 'Spanish': 'es'
}

texts = {
    'Homepage': {
        'en': '''
        # PyDF Annotation Extractor

        - This webapp aims to extract notes and higlights from PDF files.
        - The results are downloaded in a zipped file.
        ''',
        'pt_br': '''
        # PyDF Annotation Extractor

        - Esse site tem por objetivo extrair anotações de arquivos PDF
        - Os resultados são baixados em um arquivo zipzado.
        '''
    },
    'tabExtract':{
        'en': 'Files and settings',
        'pt_br': 'Arquivos e configurações'
    },
    'tabPDFtest': {
        'en': 'PDF example',
        'pt_br': 'PDF de exemplo'
    },
    'textPDFtest': {
        'en': '''
        # Illustrative PDF
        
        The example is the following image:
        
        ![Sample PDF](test/sample.png)
        ''',
        'pt_br': '''
        # PDF ilustrativo
        
        A imagem abaixo ilustra o PDF de exemplo, visto na última aba.
        '''
    },
    'textPDFtest_continue': {
        'en': '''
       If the highlight has a comment, it will come right below the highlight as a thread.

        If the note in a highlight has the text "+", the highlighted text will be concatenated with the text in the next note.

        If the annotation is a square, an image capture of the location where the square was created is created.

        The colors are represented according to the theme. By default, red will be an attention item; green will be an issue; orange will be an example and blue will be legislation.

        The <font color="cyan">cyan color</font> will be a title. If the note is "H1", "H2", "H3" or "H4", a title representing that title will be created.

        I haven't yet created a theme that changes according to the user's choices for color and title. It is to be implemented in future versions.

        By default, the extraction order will be by the X and Y position of the annotation, so be careful with the organization: if you use a "+" note in an annotation with a different color then the two problems may occur:
        - If the previous highlight is the type that generates a callout (<font color="green">green</font>, <font color="lightblue">blue</font>, <font color="red">red </font> or <font color="orange">orange</font>), the next highlight will be concatenated into the previous callout
        - If the previous highlight is of the <font color="yellow">text type</font>, the next highlight will close a tag that does not exist, but the practical effect will be a note continuing the previous one.
        ''',
        'pt_br': '''
        Se o destaque tiver um comentário, ele virá logo abaixo do destaque como um tópico.
        
        Se a nota em um destaque tiver o texto "+", o texto em destaque será concatenado com o texto da próxima anotação.
        
        Se a anotação for um quadrado, será criada uma captura da imagem do local em que o quadrado foi criado.
        
        As cores são representadas de acordo com o tema. Por padrão, vermelho será um item de atenção; verde será questão; laranjado será exemplo e azul será legislação.
        
        A <font color="cyan">cor ciano</font> será um título. Se a nota for "H1", "H2", "H3" ou "H4", será um criado um título representando esse título.
        
        Ainda não criei um tema que muda de acordo com as opções do usuário para cor e título. Está para ser implementado em versões futuras.
        
        Por padrão, a ordem de extração será pela posição X e Y da anotação, então tome cuidado com a organização: se você usar uma nota "+" em uma anotação com a cor diferente em seguida, podem ocorrer os dois problemas:
        - Caso o destaque anterior seja do tipo que gera um callout (<font color="verde">verde</font>, <font color="blue">azul</font>, <font color="red">vermelho</font> ou <font color="orange">laranjado</font>), o próximo destaque será concatenado no callout anterior
        - Caso o destaque anterior seja do <font color="yellow">tipo de texto</font>, o próximo destaque fechará uma tag que não existe, mas o efeito prático será uma nota continuando a anterior.
        '''
    },
    'textErrorPDF': {
        'en': 'There is no PDF file',
        'pt_br': 'Não há arquivo PDF.'
    },
    'tabTemplate': {
        'en': 'Template',
        'pt_br': 'Template'
    },
    'tabExample': {
        'en': 'Example',
        'pt_br': 'Exemplo'
    },
    'textExample': {
        'en': '''
        # Example
        
        This page will show your extraction will look using the PDF example.
        ''',
        'pt_br': '''
        # Exemplo
        
        Essa página te mostra como o arquivo de anotação ficará usando usando o exemplo.
        '''
    },
    'sidebarTemplateText': {
        'en': 'What type of extraction do you want?',
        'pt_br': 'Qual tipo de extração você quer?'
    },
    'sidebarTemplateChoose':{
        'en': 'Which template do you want to use?',
        'pt_br': 'Qual template você deseja.'
    },
    'sidebarLanguageChoose':{
        'en': 'Which language do you want?',
        'pt_br': 'Qual lingua você deseja usar?'
    },
    'btnSendFile': {
        'en': 'Send your file here!',
        'pt_br': 'Envie seus arquivos aqui!'
    }
}
