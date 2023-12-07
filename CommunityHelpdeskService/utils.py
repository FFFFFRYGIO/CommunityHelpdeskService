from django.core.files.storage import FileSystemStorage
from decouple import config
from openai import OpenAI


def save_files(requested_files):
    """ file saving function """
    fs = FileSystemStorage()
    for file_name in requested_files:
        file = requested_files[file_name]
        fs.save(file.name, file)


def generate_report_title(description):
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
        messages=[{"role": "user", "content": chat_content}],
        model="gpt-3.5-turbo",
    )

    response = chat_completion.choices[0].message.content

    if response[0] == '"':
        response = response[1:]

    if response[-1] == '"':
        response = response[:-1]

    return response
