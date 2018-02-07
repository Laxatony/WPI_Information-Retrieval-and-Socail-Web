# homework 1
# goal: tokenize, index, boolean query
# exports: 
#   student - a populated and instantiated ir4320.Student object
#   Index - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents


# ########################################
# first, create a student object
# ########################################

import cs525
import PorterStemmer

MY_NAME = "Yao Chun Hsieh"
MY_ANUM  = 462217691 # put your WPI numerical ID here
MY_EMAIL = "yhsieh2@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = [ 
    ('NA', 'NA'),  
    ('NA', 'NA'),
    ]

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "I do not lie, cheat or steal, or tolerate those who do."
I_AGREE_HONOR_CODE = True

# this defines the student object
student = cs525.Student(
    MY_NAME,
    MY_ANUM,
    MY_EMAIL,
    COLLABORATORS,
    I_AGREE_HONOR_CODE
    )


# ########################################
# now, write some code
# ########################################

# our index class definition will hold all logic necessary to create and search
# an index created from a directory of text files 
class Index(object):
    def __init__(self):
        # _inverted_index contains terms as keys, with the values as a list of
        # document indexes containing that term
        self._inverted_index = {}
        # _documents contains file names of documents
        self._documents = []
        # example:
        #   given the following documents:
        #     doc1 = "the dog ran"
        #     doc2 = "the cat slept"
        #   _documents = ['doc1', 'doc2']
        #   _inverted_index = {
        #      'the': [0,1],
        #      'dog': [0],
        #      'ran': [0],
        #      'cat': [1],
        #      'slept': [1]
        #      }


    # index_dir( base_path )
    # purpose: crawl through a nested directory of text files and generate an
    #   inverted index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: glob.glob()
    # parameters:
    #   base_path - a string containing a relative or direct path to a
    #     directory of text files to be indexed
    def index_dir(self, base_path):
        num_files_indexed = 0

        import glob
        for filename in glob.glob(base_path + '*.txt'):

            '''
            # Get File Encoding Information
            import chardet
            with open(filename, 'rb') as f:
                rawdata = f.read()
                detector = chardet.detect(rawdata)
            f.close()
            encoding = detector['encoding']
            '''

            # Open file with correct encoding, tokenize the text
            with open(filename, encoding='UTF-8') as f:
                
                # Get Document Name from completed file path
                docName = filename[(filename.rfind('\\')+1) : ]
                self._documents.append(docName)
                currentIndexOfDoc = len(self._documents) - 1

                # Read file and do tokenization 
                text = f.read()
                tokens = self.tokenize(text)
                tokens = self.stemming(tokens)

                # Remove duplicated term
                tokens = list(set(tokens))

                # update index
                for token in tokens:
                    if token in self._inverted_index:
                        self._inverted_index[token].append(currentIndexOfDoc)
                    else:
                        self._inverted_index[token] = [currentIndexOfDoc]
            f.close()

            num_files_indexed += 1

        return num_files_indexed

    # tokenize( text )
    # purpose: convert a string of terms into a list of tokens.        
    # convert the string of terms in text to lower case and replace each character in text, 
    # which is not an English alphabet (a-z) and a numerical digit (0-9), with whitespace.
    # preconditions: none
    # returns: list of tokens contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        tokens = []
        
        # Turn text into lowercase, 
        # Keep only legal strings as tokens.
        # Finally, remove empty elements from result tokens.
        text = text.lower()
        
        import re
        tokens = re.split(r'[^a-z0-9]', text)
        tokens = list(filter(None, tokens))

        return tokens

    # purpose: convert a string of terms into a list of tokens.        
    # convert a list of tokens to a list of stemmed tokens,     
    # preconditions: tokenize a string of terms
    # returns: list of stemmed tokens
    # parameters:
    #   tokens - a list of tokens
    def stemming(self, tokens):
        stemmed_tokens = []

        p = PorterStemmer.PorterStemmer()
        for token in tokens:
            stemmed_tokens.append(p.stem(token, 0, len(token)-1))
            
        return stemmed_tokens
    
    # boolean_search( text )
    # purpose: searches for the terms in "text" in our corpus using logical OR or logical AND. 
    # If "text" contains only single term, search it from the inverted index. If "text" contains three terms including "or" or "and", 
    # do OR or AND search depending on the second term ("or" or "and") in the "text".  
    # preconditions: _inverted_index and _documents have been populated from
    #   the corpus.
    # returns: list of document names containing relevant search results
    # parameters:
    #   text - a string of terms
    def boolean_search(self, text):
        results = []
        
        # tokenize search target
        tokens = self.tokenize(text)
        tokens = self.stemming(tokens)
        
        # get result by condition
        if len(tokens) == 1:
            token = tokens[0]

            docIndexes = self.getPostingList(token)
            for index in docIndexes:
                results.append(self._documents[index])
        else:
            docIndexes_final = []

            token = tokens[0]
            docIndexes_A = self.getPostingList(token)
            token = tokens[2]
            docIndexes_B = self.getPostingList(token)
            
            operator = tokens[1]
            if operator == 'and':
                docIndexes_final = list(set(docIndexes_A).intersection(docIndexes_B))
            else: # or
                docIndexes_final = docIndexes_A + docIndexes_B
                docIndexes_final = list(set(docIndexes_final))
                docIndexes_final = sorted(docIndexes_final)

            for index in docIndexes_final:
                results.append(self._documents[index])

        return results

    # getPostingList( token )
    # purpose: get corresponding posting list of the token if the token has been indexed  
    # preconditions: _inverted_index and _documents have been populated from
    #   the corpus.
    # returns: list of document indexes containing relevant token
    # parameters:
    #   token - a string
    def getPostingList(self, token):
        resultList = []
        if token in self._inverted_index:
                resultList = self._inverted_index[token]
        return resultList

# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = Index()
    print("starting indexer")
    num_files = index.index_dir('data/')
    print("indexed %d files" % num_files)
    for term in ('football', 'mike', 'sherman', 'mike OR sherman', 'mike AND sherman'):
        results = index.boolean_search(term)
        print("searching: %s -- results: %s" % (term, ", ".join(results)))

# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

