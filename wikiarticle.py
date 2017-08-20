"""
The script fetches an article from English Wikipedia and extracts the
most informative sentences of the article.

Ignore sections like "See also", "References", "Further reading", and
"External links".

TODO: use a better sentence tokenizer, which can detect abbreviations
      correctly
"""

import json
import sys
import urllib.parse

from summarizer import ModifiedLuhnSummarizer

API_URL = 'https://en.wikipedia.org/w/api.php'
API_PARAMS = {
    'action': 'query',
    'exlimit': 1,
    'explaintext': '',
    'format': 'json',
    'formatversion': 2,
    'prop': 'extracts'
    # 'titles': '%s'
}

IGNORED_SECTIONS = {
    "See also",
    "References",
    "Further reading",
    "External links"
}


def fetch_article(title):
    """Downloads and return the title and text of the article."""
    params = API_PARAMS.copy()
    params['titles'] = title
    url = API_URL + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as f:
        data = json.loads(f.read())
        page = data.get('query', {}).get('pages', [{}])[0]
        return page.get('title', ''), page.get('extract', '')


def extract_article_sections(text):
    """ Returns a list of dictionaries with a heading and text. """
    if not text:
        return
    sections = []
    section_heading = ''
    section_lines = []
    for line in text.split('\n'):
        if line.startswith('='):
            sections.append({
                'heading': section_heading,
                'text': '\n'.join(section_lines).strip()
            })
            section_heading = line.strip('=').strip()
            section_lines = []
        else:
            section_lines.append(line)
    sections.append({
        'heading': section_heading,
        'text': '\n'.join(section_lines).strip()
    })
    return sections


def extract_summarized_sections(title, sections):
    """ Returns a list of sentences that are found to represent the text best.
    """
    summarizer = ModifiedLuhnSummarizer(title)
    summarized_sections = []
    for section in sections:
        # STOP as soon as we see one of the ignored sections (which usually
        # appear towards the end of the article).
        if section['heading'] in IGNORED_SECTIONS:
            break
        summarized_sections.append({
            'heading': section['heading'],
            'summary': summarizer.summarize(
                section['heading'], section['text']
            )
        })
    return summarized_sections


def get_summaries(page_name):
    title, text = fetch_article(page_name)
    sections = extract_article_sections(text)
    return extract_summarized_sections(title, sections)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: main.py Barack_Obama')
        exit()
    summaries = get_summaries(sys.argv[1])
    print(summaries)
