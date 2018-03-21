# homework 4
# goal: ranked retrieval, PageRank, crawling
# exports:
#   student - a populated and instantiated cs525.Student object
#   PageRankIndex - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents and providing a
#     ranked result set

# ########################################
# first, create a student object
# ########################################

import cs525
MY_NAME = "Yao Chun Hsieh"
MY_ANUM  = 462217691 # put your UID here
MY_EMAIL = "yhsieh2@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = [ 
    ('NA', 'NA'),
    ('NA', 'NA'),
    ]

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "An Aggie does not lie, cheat or steal, or tolerate those who do."
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
import bs4 as BeautifulSoup  # you will want this for parsing html documents
from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.parse
import numpy as np

# our index class definition will hold all logic necessary to create and search
# an index created from a web directory
#
# NOTE - if you would like to subclass your original Index class from homework
# 1 or 2, feel free, but it's not required.  The grading criteria will be to
# call the index_url(...) and ranked_search(...) functions and to examine their
# output.  The index_url(...) function will also be examined to ensure you are
# building the index sanely.

class PageRankIndex(object):
    def __init__(self):

        # _inverted_index contains terms as keys, with the values as a list of
        # document indexes containing that term
        self._inverted_index = {}
        # _documents contains file names of documents and the pageranking value
        self._documents = []
        # example:
        #   given the following documents:
        #     url1 = "the dog ran"
        #     url2 = "the cat slept"
        #   _documents = [['url1', 'pageName', ranking_value], ['url2', 'pageName', ranking_value]]
        #   _inverted_index = {
        #      'the': [0,1],
        #      'dog': [0],
        #      'ran': [0],
        #      'cat': [1],
        #      'slept': [1]
        #      }
        self._webGraph = np.empty(shape=(0,0))

    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: use BeautifulSoup and urllib
    # parameters:
    #   url - a string containing a url to begin indexing at
    def index_url(self, url):
 
        # 1. build index and web graph for the collection begining with given url
        self.__index_and_graph_builder__(url)

        # 2. Compute scores for each document using pageranking technic
        self.__computePageRankingScore__()

        # rankingScore = sorted(self._documents, key=(lambda x : -x[2]))
        # print("Ranking:")
        # for doc in rankingScore:
        #     print(doc[1], '\t', doc[2])

        return len(self._documents)

    def __index_and_graph_builder__(self, url):

        curURL = url
        cur_Index = self.__findUrlDocumentIndex__(curURL)

        # 1. Add current url information into _document and _webGraph if it is not in the _document list
        #    IF it's already exist, check its graph and do not process if it has already been set up before
        if cur_Index == -1: # not exist
            # _documents
            urlName = curURL[curURL.rfind('/')+1:]
            self._documents.append([curURL, urlName, 0.0])
            cur_Index = len(self._documents)-1

            # expend _webGraph with 1 column and 1 row
            self.__expendMatrix__()
        else: # the node is exist
            connection = self._webGraph[cur_Index]
            for num in connection:
                if num != 0: # already been set up, no further process is needed
                    return 0

        
        soup = BeautifulSoup(urlopen(curURL), 'html.parser')
        # 2. Update inverted index for current url page
        self.__updateInvertedIndex__(cur_Index, soup.get_text())

        # 3. Get external links in current url document, and add them into graph
        externalURLs = []
        for link in soup.find_all('a'):
            externalURL = urllib.parse.urljoin(curURL, link.get('href')) # completed URL

            external_Index = self.__findUrlDocumentIndex__(externalURL)

            if external_Index == -1:
                # _documents
                self._documents.append([externalURL, link.string, 0.0])
                external_Index = len(self._documents)-1

                # expend _webGraph with 1 column and 1 row
                self.__expendMatrix__()

            # Set graph connection
            self._webGraph[cur_Index][external_Index] += 1

            # Crawl the externamURL
            self.__index_and_graph_builder__(externalURL)

    def __findUrlDocumentIndex__(self, url):
        for index, document in enumerate(self._documents):
            if url == document[0]:
                return index
        return -1
    def __expendMatrix__(self):
        N = self._webGraph.shape[0]
        newGraph = np.zeros((N+1,N+1))
        newGraph[:-1,:-1] = self._webGraph
        self._webGraph = newGraph

    def __updateInvertedIndex__(self, index, text):
        # 1. get the text of current url page
        tokens = self.tokenize(text)

        # 2. Remove duplicated term
        tokens = list(set(tokens))

        # 3. Update index
        for token in tokens:
            if token in self._inverted_index:
                self._inverted_index[token].append(index)
            else:
                self._inverted_index[token] = [index]
    def __computePageRankingScore__(self):
        # print("Web Graph:")
        # print(self._webGraph)

        # print("Links in page:")
        # row, col = self._webGraph.shape
        # for i in range(row):
        #     print('%d :' % i , end=' ')
        #     for j in range(col):
        #         if self._webGraph[i][j] == 1:
        #             print(j, end=' ')
        #     print()

        # 1.Generate Transition Probability Matrix(TRM) using _webGraph
        trm = self._webGraph / self._webGraph.sum(axis=1)[:,None]
        # print("Transition Probability Matrix:")
        # print(trm)

        # 2.Set Teleporting Matrix(TM)
        num = self._webGraph.shape[0]
        tm = np.full((num, num), 1/num)
        # print("Teleporting Matrix:")
        # print(tm)

        # 3.Combine TRM and TM
        alpha = 0.1
        P = (1-alpha) * trm + alpha * tm
        # print("P = (1-alpha) * trm + alpha * tm:")
        # print(P)

        # 4.Generate Steady Status
        x = np.full(num, 1/num)
        x_new = np.full(num, 0)

        while True:
            x_new = np.dot(x, P)
            if np.array_equal(x_new, x):
                break
            x = x_new
        # print("Steady ranking score:")
        # print(x_new)

        # 5.Update page rank score for each document in _document
        for index, score in enumerate(x_new):
            self._documents[index][2] = score

        # print("Ranking:")
        # for doc in self._documents:
        #     print(doc[1], doc[2])

    # tokenize( text )
    # purpose: convert a string of terms into a list of terms 
    # preconditions: none
    # returns: list of terms contained within the text
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

    # ranked_search( text )
    # purpose: searches for the terms in "text" in our index and returns
    #   AND results for highest 10 ranked results
    # preconditions: .index_url(...) has been called on our corpus
    # returns: list of tuples of (url,PageRank) containing relevant
    #   search results
    # parameters:
    #   text - a string of query terms
    def ranked_search(self, text):
        result = []

        # 1. Tokenize text into tokens
        tokens = self.tokenize(text)

        # 2. Get posting list for each token and add to pool
        docIndexList = []
        for token in tokens:
            docIndexs = self.__getPostingList__(token)
            docIndexList.append(docIndexs)

        # 3. Get final docIndexList by getting intersection of lists(sort)
        docIndexList = sorted(set.intersection(*map(set, docIndexList)))

        # 4. Get real data from _documnet[]
        for docIndex in docIndexList:
            result.append((self._documents[docIndex][0], self._documents[docIndex][2]))

        # 5. Sort by Page Rank score, and keep only top10 for required output
        result = sorted(result, key = lambda x: -x[1])
        result = result[:10]

        return result

    # getPostingList( token )
    # purpose: get corresponding posting list of the token if the token has been indexed  
    # preconditions: _inverted_index and _documents have been populated from
    #   the corpus.
    # returns: list of document indexes containing relevant token
    # parameters:
    #   token - a string
    def __getPostingList__(self, token):
        resultList = []
        if token in self._inverted_index:
                resultList = self._inverted_index[token]
        return resultList


# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = PageRankIndex()
    #url = 'http://web.cs.wpi.edu/~kmlee/cs525/new30/index.html' 
    url = 'http://web.cs.wpi.edu/~kmlee/cs525/new10/index.html'
    num_files = index.index_url(url)
    search_queries = (
       'palatial', 'college ', 'palatial college', 'college supermarket', 'famous aggie supermarket'
        )
    for q in search_queries:
        results = index.ranked_search(q)
        print("searching: %s -- results: %s" % (q, results))

# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

