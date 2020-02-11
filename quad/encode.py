# https://stackoverflow.com/questions/53589601/google-app-engine-python-3-7-build-error-pip-download-wheels-returned-code-1


with open('requirements.txt', 'rb') as source_file:
    contents = source_file.read()

with open('requirements.txt', 'w+b') as dest_file:
    dest_file.write(contents.decode('utf-16').encode('utf-8'))
