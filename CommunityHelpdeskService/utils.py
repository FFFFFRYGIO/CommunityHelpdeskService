from django.core.files.storage import FileSystemStorage


def save_files(requested_files):
    """ file saving function """
    fs = FileSystemStorage()
    for file_name in requested_files:
        file = requested_files[file_name]
        fs.save(file.name, file)
