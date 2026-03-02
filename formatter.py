from pylatexenc.latex2text import LatexNodes2Text

latex_converter = LatexNodes2Text()


def latex_to_text(s):
    return latex_converter.latex_to_text(s)


def authors(authors, highlight):
    # Output
    formatted = []
    # Clean string
    # authors = authors.replace("{", "").replace("}", "")
    # Split authors
    authors = [a.strip() for a in authors.split(" and ")]

    for a in authors:
        # Revert
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
            name = f"{first} {last}"
        else:
            name = a

        name = latex_to_text(name)

        if name.lower().endswith(highlight.lower()):
            formatted.append(f"***{name}***")
        else:
            formatted.append(f"*{name}*")

    return ", ".join(formatted)


def title(title):
    return '**' + latex_to_text(title) + '**'


def book(book, year):
    return latex_to_text(book).replace(f'{year} ', '')
