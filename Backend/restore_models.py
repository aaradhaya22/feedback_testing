import glob
for f in glob.glob('feedback_app/models/*.py'):
    with open(f, 'r') as file:
        content = file.read()
    if 'managed = True' in content:
        with open(f, 'w') as file:
            # Change back to managed = False
            file.write(content.replace('managed = True', 'managed = False'))
