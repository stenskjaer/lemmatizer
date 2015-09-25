#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unicodedata import normalize
from sys import argv
import re
import logging


def recursive_string_find(pattern, string, where_should_I_start=0):
    """Recursive search function.

    Returns list of indices of `pattern` in `string`.
    """
    pos = string.find(pattern, where_should_I_start)
    if pos == -1:
        # Not found!
        return []

    # No need for else statement
    return [pos] + recursive_string_find(pattern, string, pos + len(pattern))


# def find_lemmas_in_list(token, lemma_list):
#     """Find the first word of a lemma list line which will therefore
#     represent the lemma of the searched token

#     Keyword Arguments:
#     tokens -- list of tokens to be matched with lemmas
#     """

#     token = ' ' + token.strip() + ' '
#     # lemma_lines = [line for line in lemma_list if ' ' + token.strip() + ' ' in line]
#     def present_in_line(sequence, value):
#         for element in sequence:
#             if value in element: yield element

#     lemma_lines = present_in_line(lemma_list, token)

#     # lemma_lines = list(line for line in lemma_list if token in line)
#     lemmas = [line.split(' ')[0] for line in lemma_lines]

#     return(lemmas)

def find_lemmas(token, lemma_string):
    """Find all the possible lemma suggestions to one token. Input the
    need and haystack, the token that needs to be parsed, and the list
    of lemmas.

    Returns a list of possible lemmas.
    """

    result_list = []
    token = ' ' + token.strip() + ' '
    lemma_list = recursive_string_find(token, lemma_string)
    for item in lemma_list:
        previous_linebreak = lemma_string.rfind('\n', item-5000, item)
        match = lemma_string[previous_linebreak:previous_linebreak+40].split(' ')[0]
        result_list.append(match)

    return(result_list)

def clean_matches(dictionary_of_matches):
    """Function for counting instances of line references in the
    dictionary of matches created by the lemmatization function.  This
    function uses defaultdict to count items in list. See
    https://docs.python.org/2/library/collections.html#defaultdict-objects
    """
    from collections import defaultdict

    matches = {}
    for lemma in dictionary_of_matches:
        counter = defaultdict(int)
        for line in dictionary_of_matches[lemma]:
            counter[line] += 1

        line_refs = []
        for item in counter.items():
            if item[1] > 1:
                line_refs.append('{0} ({1})'.format(item[0], item[1]))
            else:
                line_refs.append(item[0])

        matches[lemma] = ', '.join(line_refs)

    return(matches)


def read_file(filehandle):
    """Open, read and normalize encoding of file and return the content as
    string
    """
    logging.debug('Opening and normalizing {}.'.format(filehandle))
    with open(filehandle, 'r') as f:
        content_read = f.read()
        content_normalized = normalize('NFC', content_read.decode('utf-8'))

    return(content_normalized)


def normalize_greek_accents(text):
    """Sanitize text for analysis. Includes making turning grave accents
    into acutes, making the whole text lowercase and removing
    punctuation (.,·)
    """

    # Switch graves to acutes
    text = text.replace(u'ὰ', u'ά')
    text = text.replace(u'ὲ', u'έ')
    text = text.replace(u'ὶ', u'ί')
    text = text.replace(u'ὸ', u'ό')
    text = text.replace(u'ὺ', u'ύ')
    text = text.replace(u'ὴ', u'ή')
    text = text.replace(u'ὼ', u'ώ')

    text = text.replace(u'ἃ', u'ἅ')
    text = text.replace(u'ἓ', u'ἕ')
    text = text.replace(u'ὃ', u'ὅ')
    text = text.replace(u'ἳ', u'ἵ')
    text = text.replace(u'ὓ', u'ὕ')
    text = text.replace(u'ἣ', u'ἥ')
    text = text.replace(u'ὣ', u'ὥ')

    text = text.replace(u'ἂ', u'ἄ')
    text = text.replace(u'ἒ', u'ἔ')
    text = text.replace(u'ὂ', u'ὄ')
    text = text.replace(u'ἲ', u'ἴ')
    text = text.replace(u'ὒ', u'ὔ')
    text = text.replace(u'ἢ', u'ἤ')
    text = text.replace(u'ὢ', u'ὤ')

    # Make lowercase
    text = text.lower()

    # Remove punctuation
    text = text.replace(u',', u'')
    text = text.replace(u'·', u'')

    return(text)


def add_line_numbers_to_lines(list_of_lines):
    """Return a list where excessive whitespace is removed and every item
    starts with a line number of a specific format.

    Assumptions (Should probably get resolved): 
    - That the line number is a stephanus-number (format example: `432.e.3')
    - That the very first line of the text contains such number
    """

    new_line_list = []
    last_line_mark = ""
    pattern = re.compile(r'(^\d+\.[a-e]\.)(\d+)') # matches 432.e.3
    for val, line in enumerate(content_list):
        line = re.sub('\s+', ' ', line.strip())
        match = pattern.match(line)

        if match:
            last_line_mark = match.group(1)     # e.g. 432.e.
            last_line_num = int(match.group(2)) # e.g. 3            
            since_last_mark = 0
            new_line_list.append(line)            
        else:
            since_last_mark += 1
            current_line_num = last_line_num + since_last_mark
            current_line_mark = "{0}{1}".format(last_line_mark, current_line_num)
            new_line_list.append(current_line_mark + ' ' + line)

    return(new_line_list)


def lemmatize_text(content_list, lemma_list):
    """Lemmatizes all words in text.
    Variables:
    - the text to be analyzed, split into list of lines.
    - list of lemmas

    Return:
    - dictionary of sucessfully matched terms.
    - list of terms in need of disambiguation.
    - list of terms that could not be matched.
    """
    import sys
    
    def word_count(content_list):
        """Get wordcount from list of all words in text.
        Use itertools to flatten nested list of words in lines in line_list
        """
        from itertools import chain

        word_count = len(
            list(
                chain.from_iterable(
                    [[word for word in line[8:].split(' ')] for line in content_list]
                )
            )
        )

        return(word_count)

    def print_progress(word, iteration, word_count):
        """Output the progress of the scrip to std.out.
        """
        increment = word_count / 30.0
        percent = (float(iteration) / word_count) * 100
        percent = round((iteration / float(word_count)) * 100.0, 0)
        sys.stdout.write(' ' * 80)
        sys.stdout.write('\r')
        sys.stdout.write('Analyzing {:29}'.format(
            word.encode('utf-8') + ' '* (29 - len(word))))
        sys.stdout.write('[{}{}]'.format(
            '#' * int(round(iteration / increment, 0)),
            ' ' * int(round((word_count - iteration) / increment, 0))))
        sys.stdout.write(' {:2.0f} %\r'.format(percent))
        sys.stdout.flush()


    def add_to_dict(key, value, dict):
        """Add the word to the dictionary of matched. If there is no entry,
        create it.
        """
        if key in dict.keys():
            dict[key].append(value)
        else:
            dict[key] = [value]


    logging.debug('Initializing lemmatization function...')
    
    # First some variables
    lemmas = lemma_list
    match_dict = {}
    nomatch_list = []
    disamb_list = []
    # Hack: Add whitespace to end of disambiguation file for matching
    # of tokens in find_lemmas function
    disamb_file = read_file('disambiguation.txt').replace('\n', ' \n')

    iteration = 1
    word_count = word_count(content_list)

    # Read stopwords into list
    stopword_list = [word.strip() for word in read_file('stopwords.txt').split('\n')]


    # Run each line and word of the text
    for line in content_list:
        log.debug('Start lemmatization of the line: ' + line.encode('utf-8'))

        for word in line[8:].split(' '):
            logging.debug('Analyzing {0}'.format(word.encode('utf-8')))
            
            # Remove dots, they confuse the parser
            word = word.replace('.', '')

            # Enlighten the user
            print_progress(word, iteration, word_count)

            # Increase iteration for use in progress function
            iteration += 1

            # NB: This line numbering identification is based on the assumption of stephanus-pages!
            line_number = line[:8].strip()

            # Put all possible lemmas of token in list
            match_list = find_lemmas(word, lemmas)

            # If there is exactly one match, define the lemma and create
            # an entry in the dictionary of matches
            if len(match_list) == 1:
                lemma = match_list[0]
                log.debug('Single match in line {0}. Token: {1}; lemma: {2}.'.format(
                    line_number,
                    word.encode('utf-8'),
                    lemma.encode('utf-8'),
                ))

                # Weed out stopwords (can only be done with nonambiguous terms).
                # TODO: Implement config to eneable stopwords
                if lemma in stopword_list:
                    log.info(
                        'Skipping {0} on line {1}. Matches {2} in stopword list.'.format(
                            word.encode('utf-8'),
                            line_number,
                            lemma.encode('utf-8'),
                        )
                    )
                    continue

            # Sort into the three output lists according to amount of suggestions.            
            # No match
            if len(match_list) < 1:
                nomatch_list.append(
                    [word, line]
                )

            # Matched > 1: Disambiguation needed
            elif len(match_list) > 1:
                
                if word in disamb_file:
                    lemma = find_lemmas(word, disamb_file)[0]
                    logging.debug('Word {} in disambiguation. Registering as {}'.format(
                        word.encode('utf-8'),
                        lemma.encode('utf-8')))
                    add_to_dict(lemma, line_number, match_dict)
                else:
                    disamb_list.append(
                        [word, line, [lemma.strip() for lemma in match_list]]
                    )

            # Matched exactly one word. Add line to corresponding lemma
            # list in the dictionary of matches
            else:
                if lemma in match_dict.keys():
                    match_dict[lemma].append(line_number)
                else:
                    match_dict[lemma] = [line_number]

    match_dict = clean_matches(match_dict)

    return(match_dict, disamb_list, nomatch_list)


def output_results(matches, disamb_list, nomatch_list, filename, to_shell=True, to_file=False):
    """Function for printing the results

    """
    from time import strftime

    def lvl1(title):
        length = len(title)
        return '\n{0}\n{1}\n\n'.format(
            title,
            '=' * length,
        )

    def lvl2(title):
        length = len(title)
        return '\n{0}\n{1}\n\n'.format(
            title,
            '-' * length,
        )

    output = ''

    output += lvl1('Index of terms in {0}'.format(filename))
    output += 'Results generated on {0}\n'.format(strftime("%Y-%m-%d %H:%M:%S"))

    output += lvl2('The following terms were found in the text:')

    # sorted(matches.keys()) iterates the keys alphabetically
    for term in sorted(matches.keys()):
        if term:                # Ugly hack to solve strange occurence of empty terms
            output += '{0}: {1}'.format(
                term.encode('utf-8'),
                matches[term].encode('utf-8')
            )
    output += '\n'

    output += lvl2('The following terms need disambiguation:')
    for disamb_term in disamb_list:
        output += '{0} in {1}\n'.format(
            disamb_term[0].encode('utf-8'),
            disamb_term[1].encode('utf-8')
        )
        output += 'Suggestions: {0}\n'.format(
            ", ".join([suggestion.encode('utf-8') for suggestion in disamb_term[2]])
        )

    output += lvl2('The following terms could not be found:')
    for fail in nomatch_list:
        output += '{0} in {1}\n'.format(
            fail[0].encode('utf-8'),
            fail[1].encode('utf-8')
        )

    if to_shell:
        print(output)

    if to_file:
        with open('output.txt', 'w') as f:
            f.write(output)

    return(output)



if __name__ == "__main__":

    # Setup logging
    logging.basicConfig(
        filename='output.log',
        filemode='w',
        level=logging.DEBUG,
        format='%(levelname)s: %(message)s'
    )
    log = logging
    log.debug('App and logging initiated.')

    # Map command line arguments to script and filename vars
    script, filename = argv

    # Open and read the text
    content = read_file(filename)

    content = normalize_greek_accents(content)
    logging.debug('Normalize accents of the loaded text.')

    content_list = content.split("\n")
    logging.debug('Text has been split into list of lines.')

    content_list = add_line_numbers_to_lines(content_list)
    logging.debug('Line numbers added to list of lines.')

    print('Reading the dictionary, be right back ...')
    lemmas = read_file('lemmalist.txt')
    logging.debug('Lemma list read into memory')

    matches, disamb_list, nomatch_list = lemmatize_text(content_list, lemmas)

    output_results(matches, disamb_list, nomatch_list, filename, to_shell=True, to_file=True)


# TODO:
# Tæl antal forekomster i linjerne
# Standardvalg i disambiguation: Fungerer. Men find en løsning hvor disamb_list ikke skal slutte hver linje med et whitespace
