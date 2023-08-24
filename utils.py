import re
import unicodedata


def slugify(string):
    return re.sub(r'[-\s]+', '-',unicodedata.normalize('NFKD', string)
            .encode('ascii', 'ignore')
            .decode('ascii')
            .strip()
            .lower())