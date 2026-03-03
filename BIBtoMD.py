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
ORDER = {
    'article': 0,
    'inproceedings': 0,
    'phdthesis': 4,
    'misc': 5
}
# Names for entries sections
SECTION_NAMES = {
    0: 'International Articles & Communications in Journals, Conferences and Workshops',
    4: 'Dissertations',
    5: 'Other Communications & Datasets'
}

def type_rank(t):
    return ORDER.get(t, 6)
entries = sorted(db.entries, key=lambda e: (type_rank(e['ENTRYTYPE']), -int(e.get('year', 0))))

current_section = None

with open(os.path.join(args.output, f'{args.index}'), 'w', encoding='utf8') as mainfile:
    for entry in entries:
        # Create new sections if
        entry_type = entry['ENTRYTYPE']
        rank = type_rank(entry_type)
        if rank != current_section:
            if current_section is not None:
                mainfile.write('\n')

            current_section = rank
            mainfile.write(f'## {SECTION_NAMES[rank]}\n\n')

        # Reading entries
        # entry_type = entry['ENTRYTYPE']
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

        # Create file _links
        path = os.path.join(args.output, f'{key}_links.md')

        if os.path.isfile(path) and not args.force_overwrite:
            print(f'[IGNORED] {path}')
        else:
            with open(path, 'w', encoding='utf8') as f:
                if doi:
                    f.write(f' [🔗](https://doi.org/{doi})')
                else:
                    f.write('🚧')

        # Add files to
        mainfile.write('* {' + f'% include {key}.md %' + '}\n')
        mainfile.write('{' + f'% include {key}_links.md %' + '}')
        mainfile.write('\n')
