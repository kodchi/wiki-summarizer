"""
The module identifies the most important sentences of a Wikipedia article
sections using a modified Luhn algorithm [1]. The modifications include:
  * Rather than considering words, consider lemmas;
  * Give more weight to lemmas that appear in the article title and section
    headings;
  * Words that don't belong to the following parts of speeches are ignored:
    noun, adjective, verb, adverb;
  * TODO: incorporate word senses into calculation;
  * The first sentence of the section is considered more important than
    others;
  * The first sentence of each paragraph is considered more important than
    the other sentences of the same paragraph;

Note that the module will only work with English text.

TODO: parameterize various weights and options
TODO: ignore sentences that don't end in a punctuation so that shorter
      words are not considered as summarized sentences.
TODO: long sentences should not get too high of a vote
TODO: list items should not be considered as separate paragraphs (see
      Book#manuscripts)

[1] http://courses.ischool.berkeley.edu/i256/f06/papers/luhn58.pdf
"""

from collections import defaultdict
import math

from nltk import pos_tag, word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

STOPWORDS = set(stopwords.words('english'))
COMPRESSION_RATIO = 5  # One in this sentences is selected.


def get_wordnet_pos(tag):
    """ Get wordnet part of speech from a tag. Return None if
    nothing matches. """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    return None


def lemmatize_sentence(text):
    """ Lemmatize text while removing stopwords from the outcome """
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word, tag in pos_tag(word_tokenize(text)):
        if word.lower() in STOPWORDS:
            continue
        pos = get_wordnet_pos(tag)
        if pos:
            lemmas.append(lemmatizer.lemmatize(word, pos=pos))
    return lemmas


def get_sentence_score(sentence_lemmas, paragraph_position_in_section,
                       sentence_position_in_paragraph, lemma_counts,
                       total_lemmas_in_section, heading_unique_lemmas,
                       title_unique_lemmas):

    """Get sentence score based on a list of parameters.
    The sentence score is calculated as follows:
    * For each word the frequency of its lemma (as it appears in the section)
      is divied by the number of total lemmas. And this number is added towards
      the sentence score. For example, if the section contains 2 of the word
      "book" and 3 of the word "my" and one of the word "great"; and if the
      setence contains the words "my book", then the sentence score will be:
       3 / 6 + 2 / 6 = 5 / 6.
    * An additional score of 0.3 is added for sentences that appear at the
      beginning of the section.
    * An additional score of 0.2 is added for sentences that appear at the
      beginning of a paragraph.
    * An additional score of 0.2 is added for each lemma that appears in the
      title.
    * An additional score of 0.1 is added for each lemma that appears in the
      section heading.
    TODO: The above values are arbitrary, use values that make more sense.
    """
    score = 0
    if sentence_position_in_paragraph == 0:
        score += 0.2
        if paragraph_position_in_section == 0:
            score += 0.3
    for lemma in sentence_lemmas:
        # bonus for matching the lemmas in the title or section
        if lemma in title_unique_lemmas:
            score += 0.2
        if lemma in heading_unique_lemmas:
            score += 0.1
        if lemma in lemma_counts:
            score += lemma_counts[lemma] / total_lemmas_in_section
    return score


class ModifiedLuhnSummarizer():
    def __init__(self, title, compression_ratio=COMPRESSION_RATIO):
        """ Article title """
        self.title_unique_lemmas = set(lemmatize_sentence(title))
        self.compression_ratio = compression_ratio

    def summarize(self, heading, text):
        lemma_counts = defaultdict(int)
        total_lemmas_in_section = 0

        heading_unique_lemmas = set(lemmatize_sentence(heading))
        sentences = []
        paragraphs = text.split('\n')
        lemmatized_paragraphs = []
        for paragraph in paragraphs:
            paragraph_sentences = sent_tokenize(paragraph)
            lemmatized_sentences = []
            for sentence in paragraph_sentences:
                sentences.append(sentence)
                lemmas = lemmatize_sentence(sentence)
                for lemma in lemmas:
                    lemma_counts[lemma] += 1
                    total_lemmas_in_section += 1
                lemmatized_sentences.append(lemmas)
            lemmatized_paragraphs.append(lemmatized_sentences)

        sentence_scores = []
        sentence_index = 0
        for i, paragraph in enumerate(lemmatized_paragraphs):
            for j, sentence in enumerate(paragraph):
                score = get_sentence_score(
                    sentence, i, j, lemma_counts, total_lemmas_in_section,
                    heading_unique_lemmas, self.title_unique_lemmas
                )
                sentence_scores.append((sentence_index, score))
                # print(score, '\n    ', sentences[sentence_index])
                sentence_index += 1

        # the number of sentences to pick
        n_top = math.ceil(len(sentences) / self.compression_ratio)

        # sort sentences by the score
        sentence_scores.sort(key=lambda x: x[1], reverse=True)

        # select the positions of the top sentences
        top_sentences = {x[0] for x in sentence_scores[:n_top]}

        # extract the highest rated sentences in order they appear in text
        summary = []
        for i, sentence in enumerate(sentences):
            if i in top_sentences:
                summary.append(sentence)

        return summary
