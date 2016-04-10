#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Usage: lemmatize.py <command> [options] FILE

A script for identifying dictionary forms of words in a text based
on a full form lemma list. It is also possible to create an index
locorum based on the lemmatizations.

Arguments:
  FILE       A plain text file containing the text you want analyzed.

Commands:
  lemmatize  Lemmatize each word in the input file and return the results.
  index      Create an index locorum based on the lemmatization of the input
             file.

Options:
  -l, --lemmas <file>     A plain text file containing the lemmas to be used for
                          the analysis. This must be a full form lemma list,
                          i.e. a list where each line first contains the lemma
                          followed by all the forms of the lemma that you want
                          the script to recognize. [default: lemmalist.txt]
  -s, --stopwords <file>  A plain text file containing the words that you want
                          the script to skip. [default: stopwords.txt]
  -d, --disambiguations <file>
                          A plain text file instructing the script on which of
                          several possibilities should be preferred in need of
                          disambiguation. [default: disambiguations.txt]
  -o, --output <mode>     How do you want it served? Shell, file or both? Output
                          to file is put in a file called `output.txt` in the
                          working directory. [default: shell]
  -l, --log <level>       Set the verbosity of the log. Optional levels are
                          currently just `info` and `debug`. [default: info]
  -q, --quiet             Do you want the script to run quietly?
  -v, --version           Show script version and exit.
  -h, --help              Show this help message and exit.

For more info, see https://github.com/stenskjaer/lemmatizer.
"""

from docopt import docopt
from unicodedata import normalize
from sys import stdout
from time import strftime
import re
import logging


def recursive_string_find(pattern, string, start=0):
    """Recursive search function.

    Returns list of indices of `pattern` in `string`.
    """
    pos = string.find(pattern, start)
    if pos == -1:
        # Not found!
        return []

    # No need for else statement
    return [pos] + recursive_string_find(pattern, string, pos + len(pattern))


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
        result_list.append(match.strip())

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
    log.debug('Opening and normalizing {}.'.format(filehandle))
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
    return_list = []

    has_line_numbers = False
    if list_of_lines[0][:2] == '##':
        has_line_numbers = True

    if has_line_numbers == True:
        for line in list_of_lines:
            if line[:2] == '##':    # Contains a line number
                current_line_reference = line[2:].strip()
                reference_prefix = current_line_reference.rsplit('.', 1)[0]
                line_number = int(current_line_reference.rsplit('.', 1)[1])
                line_index = 0
                continue            # Move on to next line
            else:
                line_number += line_index
                current_line_reference = reference_prefix + str(line_number)
                line_index += 1


            return_list.append([current_line_reference, line.strip()])
    else:
        return_list = [[val + 1, line] for val, line in enumerate(list_of_lines)]

    return(return_list)


class Analyze(object):
    """A class for all analysis of the text"""

    def __init__(self, text, lemmas, disambiguations=False, stopwords=False):
        self.text = text
        self.lemmas = lemmas
        self.stopwords = [word.strip() for word in read_file(stopwords).split('\n')]
        self.disambiguations = read_file(disambiguations).replace('\n', ' \n')
        self.word_count = self.word_count(self.text)

        log.debug('Initialized an Analyze object')

    def word_count(self, text):
        """Get wordcount from list of all words in text.
        Use itertools to flatten nested list of words in lines in line_list

        return: int value of words in text
        """
        from itertools import chain

        word_count = len(
            list(
                chain.from_iterable(
                    [[word for word in line[1].split(' ')] for line in text]
                )
            )
        )

        return(word_count)

    def print_progress(self, word, iteration, word_count):
        """Output the progress of the scrip to std.out.
        """
        increment = word_count / 30.0
        percent = (float(iteration) / word_count) * 100
        percent = round((iteration / float(word_count)) * 100.0, 0)
        stdout.write(' ' * 80)
        stdout.write('\r')
        stdout.write('Analyzing {:29}'.format(
            word.encode('utf-8') + ' '* (29 - len(word))))
        stdout.write('[{}{}]'.format(
            '#' * int(round(iteration / increment, 0)),
            ' ' * int(round((word_count - iteration) / increment, 0))))
        stdout.write(' {:2.0f} %\r'.format(percent))
        stdout.flush()

    def lemmatize_text(self):
        """Lemmatizes all words in text.
        Variables used:
        - self.text: the text to be analyzed, split into list of lines.

        Return:
        - nested list of results. Each sublist either contains 1, 2 or more items. 
        1 = no match, 2 = exact match, more = more possible matches.
        """

        log.debug('Initializing lemmatization method...')

        # Initiate vars: match_list and results
        match_list = []
        results = []

        # Set the iteration for the progress bar
        iteration = 1

        # Run each line and word of the text
        for line in self.text:
            log.debug('Start lemmatization of the line: ' + line[1].encode('utf-8'))

            for word in line[1].split(' '):
                log.debug('Analyzing {0}'.format(word.encode('utf-8')))

                # Remove dots, they confuse the parser
                word = word.replace('.', '')

                # Enlighten the user
                self.print_progress(word, iteration, self.word_count)

                # Increase iteration for use in progress function
                iteration += 1

                # Put all possible lemmas of token in list
                match_list = find_lemmas(word, self.lemmas)
                log.debug('Matches for {0}: {1}'.format(
                    word.encode('utf-8'),
                    ' '.join(match_list).encode('utf-8')
                ))

                # Put the results in a list. If there is no match, it only
                # shows the token form, if there is exactly one match, the
                # token and the lemma are contained in the list, if there
                # are more possible lemmas, then the token occurs first,
                # followed by any amount of possible lemmas.
                results.append([word] + match_list)


                # # Matched > 1: Disambiguation needed
                # elif len(match_list) > 1:

                #     if word in disamb_file:
                #         lemma = find_lemmas(word, disamb_file)[0]
                #         log.debug('Word {} in disambiguation. Registering as {}'.format(
                #             word.encode('utf-8'),
                #             lemma.encode('utf-8')))
                #         match_list.append(word, lemma)
                #     else:
                #         disamb_list.append(
                #             [word, line[1], [lemma.strip() for lemma in match_list]]
                #         )

        return(results)

    def create_index(self):
        """Lemmatizes all words in text.
        Variables used:
        - self.text: the text to be analyzed, split into list of lines.
        - self.lemmas: list of lemmas
        - self.disambiguations: list of disambiguation terms

        Return:
        - dictionary of sucessfully matched terms.
        - list of terms in need of disambiguation.
        - list of terms that could not be matched.
        """

        def add_to_dict(key, value, dict):
            """Add the word to the dictionary of matched. If there is no entry,
            create it.
            """
            if key in dict.keys():
                dict[key].append(value)
            else:
                dict[key] = [value]

        log.debug('Initializing lemmatization method...')

        # First some variables
        match_dict = {}
        nomatch_list = []
        disamb_list = []

        iteration = 1

        # Run each line and word of the text
        for line in self.text:
            log.debug('Start lemmatization of the line: ' + line[1].encode('utf-8'))

            for word in line[1].split(' '):
                log.debug('Analyzing {0}'.format(word.encode('utf-8')))

                # Remove dots, they confuse the parser
                word = word.replace('.', '')

                # Enlighten the user
                self.print_progress(word, iteration, self.word_count)

                # Increase iteration for use in progress function
                iteration += 1

                # Get the line number
                line_number = str(line[0])

                # Put all possible lemmas of token in list
                match_list = find_lemmas(word, self.lemmas)

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
                    # TODO: Implement config to enable stopwords
                    if lemma in self.stopwords:
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
                        [word, line[1]]
                    )

                # Matched > 1: Disambiguation needed
                elif len(match_list) > 1:

                    if word in self.disambiguations:
                        lemma = find_lemmas(word, self.disambiguations)[0]
                        log.debug('Word {} in disambiguation. Registering as {}'.format(
                            word.encode('utf-8'),
                            lemma.encode('utf-8')))
                        add_to_dict(lemma, line_number, match_dict)
                    else:
                        disamb_list.append(
                            [word, line[1], [lemma.strip() for lemma in match_list]]
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


class Output(object):
    """Output the input according to a given method."""

    def __init__(self, output=False):
        self.output = output

    def return_output(self, output_string):
        """Return the output to stdout, file or both, according to optional arguments."""

        if self.output == 'shell':
            print(output_string)
        elif self.output == 'file':
            with open('output.txt', 'w') as f:
                f.write(output_string)
        elif self.output == 'both':
            print(output_string)
            with open('output.txt', 'w') as f:
                f.write(output_string)

    def lvl1(self, title):
        """Format a level 2 markdown title and return it as string."""
        length = len(title)
        return '\n{0}\n{1}\n\n'.format(
            title,
            '=' * length,
        )

    def lvl2(self, title):
        """Format a level two markdown title and return it as string."""
        length = len(title)
        return '\n{0}\n{1}\n\n'.format(
            title,
            '-' * length,
        )

    def output_index(self, matches, disamb_list, nomatch_list, filename):
        """Format the results of index method for printing, and return as
        string.

        """
        try:
            from pyuca import Collator
        except ImportError:
            exit('Error: To output the index we need `pyuca` to sort the unicode '
                 'text properly. Run `pip install pyuca` and try again.')

        output = self.lvl1('\nIndex of terms in {0}'.format(filename))
        output += 'Results generated on {0}\n'.format(strftime("%Y-%m-%d %H:%M:%S"))
        output += self.lvl2('The following terms were found in the text:')

        # sorted(matches.keys()) iterates the keys alphabetically. Uses
        # pyuca to sort the Greek properly. See https://github.com/jtauber/pyuca
        c = Collator()
        for term in sorted(matches.keys(), key=c.sort_key):
            if term:       # Ugly hack to solve strange occurence of empty terms
                output += '{0}: {1}'.format(
                    term.encode('utf-8'),
                    matches[term].encode('utf-8')
                )
        output += '\n'

        output += self.lvl2('The following terms need disambiguation:')
        for disamb_term in disamb_list:
            output += '{0} in {1}\n'.format(
                disamb_term[0].encode('utf-8'),
                disamb_term[1].encode('utf-8')
            )
            output += 'Suggestions: {0}\n'.format(
                ", ".join([suggestion.encode('utf-8') for suggestion in disamb_term[2]])
            )

        output += self.lvl2('The following terms could not be found:')
        for fail in nomatch_list:
            output += '{0} in {1}\n'.format(
                fail[0].encode('utf-8'),
                fail[1].encode('utf-8')
            )

        self.return_output(output)

    def output_lemmas(self, matches, filename):
        """Format the results of lemmatization for printing, and return as
        string.

        """

        output = self.lvl1('\nLemmas of terms in {0}'.format(filename))
        output += 'Results generated on {0}\n'.format(strftime("%Y-%m-%d %H:%M:%S"))

        for match in matches:
            output += ' '.join(match).encode('utf-8') + '\n'

        self.return_output(output)


if __name__ == "__main__":

    # Read command line arguments
    args = docopt(__doc__, version='0.0.9')

    # Setup logging
    loglevel = args['--log']
    logging.basicConfig(
        filename='output.log',
        filemode='w',
        level=getattr(logging, loglevel.upper()),
        format='%(levelname)s: %(message)s'
    )
    log = logging
    log.info('App and logging initiated.')

    # Map command line arguments to script and filename vars
    filename = args['FILE']

    # Open and read the text
    content = read_file(args['FILE'])

    content = normalize_greek_accents(content)
    log.debug('Normalized accents of the loaded text.')

    content_list = content.split("\n")
    log.debug('Text has been split into list of lines.')

    print('Reading the dictionary, be right back ...')
    lemmas = read_file(args['--lemmas'])
    log.debug('Lemma list read into memory')

    content_list = add_line_numbers_to_lines(content_list)
    log.debug('Line numbers added to list of lines.')

    # Initialize the objects for analysis and output
    analysis = Analyze( content_list, lemmas,
                        disambiguations=args['--disambiguations'],
                        stopwords=args['--stopwords'] )
    output = Output(args['--output'])
                                                                                                            
    if args['<command>'] == 'index':
        log.debug('Index mode selected.')
        matches, disamb_list, nomatch_list = analysis.create_index()
        output.output_index(matches, disamb_list, nomatch_list, filename)
    elif args['<command>'] == 'lemmatize':
        log.debug('Lemmatization mode selected.')
        match_list = analysis.lemmatize_text()
        output.output_lemmas(match_list, filename)

    log.info('Results returned sucessfully.')
