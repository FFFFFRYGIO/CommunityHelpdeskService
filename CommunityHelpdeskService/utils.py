from enum import Enum

from decouple import config
from django.core.files.storage import FileSystemStorage
from openai import OpenAI


def save_files(requested_files: list) -> None:
    """ file saving function """
    fs = FileSystemStorage()
    for file_name in requested_files:
        file = requested_files[file_name]
        fs.save(file.name, file)


def generate_report_title(description: str) -> str:
    """ generate report title with chatGPT help """
    client = OpenAI(api_key=config('OPENAI_API_KEY'))
    language = config('SYS_LANG')
    if language == 'pl':
        chat_content = (f'Stwórz tytuł do zgłoszenia o takim opisie: "{description}".'
                        f'Tytuł ma być zwięzły, kilkusłowny oraz pragmatyczny, bez upiększeń')
    elif language == 'en':
        chat_content = (f'Create a title of the report that has this description: "{description}".'
                        f'Title must be short, with few words and pragmatic, without additional exclamations')
    else:
        raise ValueError(f'Language "{language}" not supported')

    chat_completion = client.chat.completions.create(
        messages=[{'role': 'user', 'content': chat_content}],
        model=config('AI_MODEL'),
    )

    response = chat_completion.choices[0].message.content

    if response[0] == '"' and response[-1] == '"':
        response = response[1:-1]

    return response


class ReportStatus(Enum):
    """ Enum for report statuses """

    def __init__(self, n: int, phrase: str, is_new_article: bool, means_in_progress: bool = False,
                 editor_permitted: bool = False):
        self.n = n
        self.phrase = phrase
        self.is_new_article = is_new_article
        self.means_in_progress = means_in_progress
        self.editor_permitted = editor_permitted

    @classmethod
    def get_status_name(cls, n: int) -> str:
        """ get status phrase value to display it """
        for status in cls:
            if status.n == n:
                return status.phrase
        raise ValueError(f'Bad status number {n}')

    @classmethod
    def is_about_new_article(cls, n: int) -> bool:
        """ check if the status is about new article """
        for status in cls:
            if status.n == n:
                return status.is_new_article
        raise ValueError(f'Bad status number {n}')

    NA_OPENED = (1, 'na opened', True, True)
    NA_ASSIGNED = (2, 'na assigned', True, True, True)
    NA_CHANGES_APPLIED = (3, 'na changes applied', True, True, True)
    ARTICLE_REJECTED = (4, 'article rejected', True)

    OPENED = (5, 'opened', False, True)
    ASSIGNED = (6, 'assigned', False, True, True)
    CHANGES_APPLIED = (7, 'changes applied', False, True, True)
    REJECTED = (8, 'rejected', False)

    CONCLUDED = (9, 'concluded', False)


class ArticleStatus(Enum):
    """ Enum for article statuses """

    def __init__(self, n: int, phrase: str, search_permitted: bool = False):
        self.n = n
        self.phrase = phrase
        self.search_permitted = search_permitted

    @classmethod
    def get_status_name(cls, n: int) -> str:
        """ get status phrase value to display it """
        for status in cls:
            if status.n == n:
                return status.phrase
        raise ValueError(f'Bad status number {n}')

    APPROVED = (1, 'approved', True)
    UNAPPROVED = (2, 'unapproved', True)
    CHANGES_REQUESTED = (3, 'changes requested', True)
    CHANGES_DURING_REPORT = (4, 'changes during report', True)
    REJECTED = (5, 'rejected')
