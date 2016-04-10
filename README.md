# Lemmatizer

A modest script for identifying dictionary forms of morphological
forms in a text by the use of a full form lemma list.  It can also
create an *index verborum* for the text. It currently assumes the
scheme of Stephanus-pages known (among others) from classical editions
of the works of Plato.

It can recognize end report the line number of each term. Currently it
is only in the format of Stephanus-pages (known from text editions of
Plato and other classical authors). This should get changed soon to
accommodate a range of different line numbering schemes.

*A note on language*: I developed and used this script for Ancient
Greek. That is reflected in the default lemma, disambiguation and
stopword files. Lemma lists are, in their very nature, big and pretty
unwieldy, so I have removed the file `lemmalist.txt` from the
repository, since you might not want to use it. Should you be
interested in a greek lemma list that is based on Liddell, Scott and
Jones, I suggest (my own
repository)[https://github.com/stenskjaer/lemmalist-greek.git] since
that is complies with the format required by the script.

## Basic usage
```lemmatize.py <command> [options] FILE```

This means roughly: Call the script by its name, followed by which
command you want it to accomplish, options that modify the execution
of that action and the file you want the action performed on.

### Commands and options

```
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
```

## Lemmatize a text

To lemmatize a text, you simply call the name of the script, followed
by the command `lemmatize` and the file you want analyzed.
For example:
```lemmatize.py lemmatize textfile.txt```

The script will output a list of all the words in the text followed by
- nothing more, which means that it wasn't able to identify the
  relevant word,
- one more word, which means that this was the only lemma for the
  given form that it was able to identify, or
- two or more words, which means that these are possible lemmas for
  the given word, listen in the order they have been found in the
  lemmalist (i.e. an unprioritized list).

It goes without saying that you want as many of the items on the list
to contain *only* two words, the token form from the text and (what is
most likely) the dictionary form, the lemma, of that word. To find out
how to get a bit better results with this, see the disambiguation below.

The lemmatize-function (currently) makes no use of the line numbering
function of the script. The text you feed the script does therefore
not need any line numbers. If it does have (and they comply with the
directions given below), it won't be a problem.

## Create an index verborum to a text

Currently, the script will only be able to produce a proper index of a
text with a rather specific setup, due to the handling of line
numbers. Let's just say for now that the text has to look like the
example `testinput.txt` to work properly (or at all). Once the line
numbering scheme has been improved, this will get better documented.

## Handling line numbers

Well, this area still leaves a lot to be wanted... 

## Formatting lemma, disambiguation, and stopword lists

The quality of the identification of lemmas relies completely on
quality of the provided lemma list. You can improve the performance
a bit with well chosen disambiguations.

Lemma and disambiguation lists are expected to be formatted in the same
way: First the lemma you want to identify or disambiguate, one or more
space characters and the word(s) you want to be identified with that
lemma.


### Lemma list

An example:

```
eat eat eats ate eating eaten
read read reads reading
```
This would be is a lemma list for en English text with a very limited
vocabulary. Any forms of ‘to eat’ or ‘to read’ would be recognized by
the script.


### Disambiguation lists

In case of some ambiguous words, you might find yourself wanting to
tell the script which of the possibilities it should prefer. This
could either be the case if some dialect forms of different words
create ambiguities that you know wont apply to your text. 

Let's take an example. In Ancient Greek the word term οὖν would in
very many cases be the conclusive conjunction meaning ‘therefore,
hence’ and the like, but it also happens to be the an Ionic form of
the imperfect participle of εἶναι (which would usually look like
ὤν). If you know (or can reasonably assume) that that specific form,
and the ambiguity it involves, will not occur in your text (if for
instance it is written in the Attic dialect), you can add an item to
your disambiguation list.

You can of course also add disambiguations to your list although both
lemmas might occur in you text, but you can live with that slight
inaccuracy of the analysis, knowing that you won't have to
disambiguate 500 forms where 498 of them all refer to one of the
possible lemmas. An example of that (again from Ancient Greek) would
be the form ἄν. It would often refer to the modal particle of the same
form, but it could also, in very rare cases, refer to the poetic form
of the preposition ἀνά. 

Disambiguation lists can be dangerous. You need to know which lemmas
you actually disambiguate. To return to our last example with ἄν, it
might also refer to the contracted form of ἐάν, which again is a form
of εἰ ἄν, that is a combination of the conditional particle εἰ and the
mentioned modal particle. You might not want that listed as simply the
modal particle!

*Warning:* The example lemma list contains “unsafe”
disambiguations. They are illustrative. A good disambiguation list
might require a couple of runs of the script and subsequent analysis
of the results.

### Stop words

Finally, you might want to skip some words. Simply add those to a file
that you refer to with the option `--stopwords`, with one word per
line.

## Languages

The script has been written for indexing and lemmatizing Ancient
Greek. This means that it should be able to handle any Unicode
formatted text you feed it, but this has not been tested.


## Caveats

This is currently not a particularly efficient implementation. Not
surprisingly, performing a recursive search in a very large text file
to find any amount of matches for at particular word form is a pretty
intensive task. Analyzing a just a relatively long text (say 10.000
words) of a heavily inflected language against an extensive lemma list
will be a time consuming task.

# Use as python module in your script

This is not implemented yet...

# To-do for the README
 - [ ] Do a bit of performance testing to see how it performs with
   larger files.
 - [ ] Document the index locorum function.
 - [ ] Document the line numbering scheme.
