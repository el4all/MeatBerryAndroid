import json

a = 'qw33'
print(a[2:])
def open_and_read_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)

        return data

def write_json(file_output, data):
    with open(file_output, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        print('Wrote')