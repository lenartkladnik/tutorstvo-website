import re

contents = ""
final = []

with open("ucilnice.txt", "r") as f:
    contents = f.read().replace('?', 'č')
    contents = contents.split('\n')[1:]

for s in contents:
    t = re.findall(r'(?:[^\s,]+(?:, [^\s,]+)*)', s) # Remove multi spaces and format

    if t:
        t[2] = t[2].replace('(', '').replace(')', '')
        if len(t) > 3:
            t[3] = f'"{t[3].replace(', ', ',')}"'

        else:
            t.append('""')

        final.append(t)

with open("ucilnice.csv", "w") as f:
    for s in final:
        f.write(','.join(s))
        f.write('\n')
