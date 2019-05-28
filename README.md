# Kathy Kwon

# Purpose:
	The purpose of this project is to create a program that reads in text documents, 
	and generates a .csv file containing the most frequently used words of 
	the combined documents. 
	This program keeps track of the word, frequency, the part of speech, which 
	document(s) each word is used in, and up to three sentences where the word is used.


# Things you need to run:
	- NLTK:
		Step 1: pip install -U nltk
		Step 2: Open Python interpreter and type comnmands:
					>> import nltk
					>> nltk.download()
		Step 3: A GUI should pop up; download all packages


# Command to run:
	$ python word_generator.py
		(This will use the default documents of doc1.txt, doc2.txt, doc3.txt, doc4.txt,
		doc5.txt, doc6.txt and default number of frequently used words of 20)
	
	$ python word_generator.py --doc {document_names} --num {number of words}

	$ python word_generator.py --help

	- Example:
		$ python word_generator.py --doc doc1.txt doc2.txt --num 10
			(This will read in doc1.txt and doc2.txt and generate the combined 10 most
			frequently used words from both documents)


# Known issues:
	- Some word frequencies are inaccurate due to part of speech tagging; verb tagging is more strict than others
		==> Example: "one"; freq 2; noun ==> but adjective uses of "one" appear in sentences
		==> Solution: Tag every single word of every sentence, and match based on word (original and lemmatized) as well as part of speech


# Room for growth:
	- Tinker with word stemming
	- Filter output based on specific parts of speech
	- Create a GUI
	- Verb filtering