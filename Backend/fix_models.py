import glob
for f in glob.glob('feedback_app/models/*.py'):
    with open(f, 'r') as file:
        content = file.read()
    if 'managed = False' in content:
        with open(f, 'w') as file:
            # Change to managed = True to allow migration
            file.write(content.replace('managed = False', 'managed = True'))
