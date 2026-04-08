import os
directory = './Card_Images'
try:
    for filename in os.listdir(directory):
        name, ext = os.path.splitext(filename)
        if name.endswith('2'):
            new_name = name[:-1] + ext
            os.rename(f'{directory}/{filename}', f'{directory}/{new_name}')
            print(f"Renamed: {filename} → {new_name}")
    print(len(os.listdir(directory)))
except Exception as e:
    print(f"An error occurred: {e}")

