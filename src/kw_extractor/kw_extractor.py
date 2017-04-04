import rake
import operator


class extractor:
    def __init__(self, abstractFile):
        self.abstractFile       =   abstractFile
        self.noOfCharacters     =   5       # Each word has at least 5 characters
        self.maxNoOfWords       =   3       # Each phrase has at most 3 words
        self.minNoOfWords       =   3       # Each keyword appears in the text at least 3 times

    def rake_extract(self):
        abstractFile    =   self.abstractFile
        noOfCharacters  =   self.noOfCharacters
        maxNoOfWords    =   self.minNoOfWords
        minNoOfWords    =   self.minNoOfWords

        keyword_list   =   []

        rake_object     =   rake.Rake("data/stoplists/SmartStoplist.txt", noOfCharacters, maxNoOfWords, minNoOfWords)

        # If test_file is a list containing pubmed abstracts
        # for abstracts in abstractFile:
        #     keywords    =   rake_object.run(abstracts)
        #     keyword_list.append(keywords)

        keywords        =   rake_object.run(abstractFile)
        print "Keywords: ", keywords



test_file       =   open("data/testData/pubmedtest.txt", 'r')
text            =   test_file.read()
extractorObject =   extractor(text)
keywords        =   extractorObject.rake_extract()