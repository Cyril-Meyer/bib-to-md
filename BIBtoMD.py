import argparse
import os
import bibtexparser
import formatter

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('filename',
                    help='BibTeX file')
parser.add_argument('author',
                    help='Author name to highlight')
parser.add_argument('--output', default='output',
                    help='Output folder')
parser.add_argument('--index', default='publications.md',
                    help='Output file including others')
parser.add_argument('--force-overwrite', action='store_true')
args = parser.parse_args()

# Read and parse input bib
with open(args.filename) as f:
    db = bibtexparser.load(f)

# Create output folder if required
if not os.path.exists(args.output):
    os.makedirs(args.output)

# Sorting entries
def type_rank(t):
    if t in ('article', 'inproceedings'):
        return 0
    if t == 'phdthesis':
        return 4
    return 5
entries = sorted(db.entries, key=lambda e: (type_rank(e['ENTRYTYPE']), -int(e.get('year', 0))))

with open(os.path.join(args.output, f'{args.index}'), 'w', encoding='utf8') as mainfile:
    for entry in entries:
        # Reading entries
        entry_type = entry['ENTRYTYPE']
        key = entry['ID']
        authors = entry['author']
        title = entry['title']
        year = entry['year']

        doi = False
        if entry_type != 'phdthesis':
            doi = entry['doi']

        book = False
        if entry_type == 'inproceedings':
            book = entry['booktitle']
        elif entry_type == 'article':
            book = entry['journal']
        elif entry_type not in ['misc', 'phdthesis']:
            raise NotImplementedError

        # Creating output
        path = os.path.join(args.output, f'{key}.md')
        # Do not touch if file already exists
        if os.path.isfile(path) and not args.force_overwrite:
            print(f'[IGNORED] {path}')
        else:
            with open(path, 'w', encoding='utf8') as f:
                f.write(formatter.authors(authors, args.author))
                f.write(' : ')
                f.write(formatter.title(title))
                f.write('. ')
                if book:
                    f.write(f'{formatter.book(book, year)}, ')
                f.write(f'{year}.')
                if doi:
                    f.write(f' [{doi}](https://doi.org/{doi}).')
                f.write('  ')

        # Create file _links if not existing.
        open(os.path.join(args.output, f'{key}_links.md'), 'a').close()

        # Add files to
        mainfile.write('* {' + f'% include_relative {key}.md %' + '}')
        mainfile.write('{' + f'% include_relative {key}_links.md %' + '}')
        mainfile.write('\n')
