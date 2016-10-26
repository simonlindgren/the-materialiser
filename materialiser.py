# coding: utf-8
print ''
print ''
print '========================'
print ''
print 'M A T E R I A L I S E R'
print ''
print '========================'
print ''
print 'Getting ready to materialise. Please wait ...'


# Fix some character encoding stuff
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

# Import modules
import re
from urlparse import urlparse
import string
from random import choice
import csv
import itertools
import pandas as pd
import io
from spacy.en import English
parser = English()


print ''
print 'Put a file named dataset.txt in the working directory.'
print 'The file should have one tweet (or similar) per line.'
raw_input("Press Enter to continue...")

# (1) Draw sample

# Open the dataset
dataset = open('dataset.txt', 'r').readlines()

# Count lines in dataset
linecount = sum(1 for line in dataset)
samplesize = round(0.1 * linecount)
print ''
print 'The dataset has ' + str(linecount) + ' lines.'
print ''
print 'We will draw a sample of 10 % of the lines, which equals ' + str(int(samplesize))
raw_input("Press Enter to continue...")

# Read the lines
lines = [a.strip() for a in dataset]

# Draw sample
result = [choice(lines) for a in range(int(samplesize))]

# Save sample
samplefile = open('sample.txt', 'w')
for r in result:
		samplefile.write(r + '\n')
print 'Sample drawn!'
print ''
samplefile.close()


# (2) Cleaning the sample

# I/O
messy = open('sample.txt', 'r')
clean = open('sample_cleaned.txt', "w")

# Cleaning
print 'Now let\'s clean the sample from hashtags, usernames, urls, punctuation, and extra whitespace.'
raw_input("Press Enter to continue...")

for line in messy:
	nohash = ' '.join(word for word in line.split(' ') if not word.startswith('#'))
	nousers = ' '.join(word for word in nohash.split(' ') if not word.startswith('@'))
	nourls = re.sub(r'(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$', "", nousers)
	#Remove punctuation
	trans_table = string.maketrans( string.punctuation, " "*len(string.punctuation))
	nopunctuation = nourls.translate(trans_table)
	# Remove extra whitespace
	tweet = " ".join(nopunctuation.split())
	# Remove blank lines
	noblanks = re.sub(r'(\n\n)','\n',tweet)
	# Save all non-empty lines
	if not len(noblanks.strip()) == 0 :
		clean.write((noblanks.lower() + '\n'))

clean.close()

print 'Sample has been cleaned!'
print ''

# (3) Extracting named entities and noun phrases

# Prepare input file and output file
infile = open('sample_cleaned.txt', 'r')
outfile = open('output-data.csv', 'w')

raw_input("Press Enter to extract Named Entities and Noun Phrases...")

# Add the items (lines) to a list
datalist = []
for line in infile: 
	datalist.append(line)

# Set an item counter
itemnumber = 0
print 'Parsing ...',
print ''

# Iterate over the items to tag named entities and extract nounphrases
for item in datalist:
	itemnumber = itemnumber + 1 #increase the counter
	#parse the item (sentence)
	#parsed = parser(unicode(item))
	parsed = parser(unicode(item).strip()) #the .strip() is important to not get extra newlines
	# Write NER stuff
	ents = list(parsed.ents)
	for entity in ents:
		
		#outfile.write(str(itemnumber) + '\t' + ' '.join(t.orth_ for t in entity) + '\t' + entity.label_ + '\n')
		# Let's write to outfile without entity labels
		outfile.write(str(itemnumber) + '\t' + ' '.join(t.orth_ for t in entity) + '\n')

	# Write NP stuff
	for np in parsed.noun_chunks:
		outfile.write(str(itemnumber) + '\t' + np.text + '\n')

print ''
print 'Named Entities and Noun Phrases have been secured!'
print ''	

outfile.close()

#(4) Generate pairs
raw_input("Press Enter to generate a list of Materialiser(TM) pairs ...")

# Remove spaces
materialised_data = open('output-data.csv', 'r')
materialised_data_string = ''.join(map(str, materialised_data))
nospace_text = re.sub(' ', '_', materialised_data_string)
nospace_file = open('nospace.txt', "w")
nospace_file.write(nospace_text)
nospace_file.close()

# Make pairs
# Get the tokens and use itertools.groupby with first column as key to group items 
# with same first column
# Once you have that, filter out the lists with one 1 item, and apply a combination on the rest.
with open('nospace.txt') as f:
	with open("#pairs.csv","wb") as f2:
		cw = csv.writer(f2,delimiter=";")
		for l in itertools.groupby((l.split() for l in f),lambda x : x[0]):
			grouped = set(x[1] for x in l[1])  # set avoids duplicate rows
			if len(grouped)>1:
				for c in itertools.combinations(grouped,2):
					cw.writerow(c)

print ''
print 'Enjoy the materialised pairs!'
print ''