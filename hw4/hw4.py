# homework 4
# goal: k-means clustering on vectors of TF-IDF values,
#   normalized for every document.
# exports: 
#   student - a populated and instantiated cs525.Student object
#   Clustering - a class which encapsulates the necessary logic for
#       clustering a set of documents by tf-idf 


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
import glob
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import numpy as np
import codecs
import math
import sys
import copy
import random
import datetime

# Our Clustering object will contain all logic necessary to crawl a local
# directory of text files, tokenize them, calculate tf-idf vectors on their
# contents then cluster them according to k-means. The Clustering class should
# select r random restarts to ensure getting good clusters and then use RSS, an
# internal metric, to calculate best clusters.  The details are left to the
# student.

class Clustering(object):
    # hint: create something here to hold your dictionary and tf-idf for every
    #   term in every document
    def __init__(self):
        self._docName = []
        self._TF_data = {}      # {'docName': {'term':amount}, 'docName': {'term':amount}}
        self._TF_iDF_data = {}  # {'docName': {'term':tf-idf}, 'docName': {'term':tf-idf}}

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
        tokens = re.split(r'[^a-z0-9]', text)
        tokens = list(filter(None, tokens))

        return tokens

    # consume_dir( path, k )
    # purpose: accept a path to a directory of files which need to be clustered
    # preconditions: none
    # returns: list of documents, clustered into k clusters
    #   structured as follows:
    #   [
    #       [ first, cluster, of, docs, ],
    #       [ second, cluster, of, docs, ],
    #       ...
    #   ]
    #   each cluster list above should contain the document name WITHOUT the
    #   preceding path.  JUST The Filename.
    # parameters:
    #   path - string path to directory of documents to cluster
    #   k - number of clusters to generate
    def consume_dir(self, path, k):
        self._docName = []
        self._TF_data = {}      # {'docName': {'term':amount}, 'docName': {'term':amount}}
        self._TF_iDF_data = {}  # {'docName': {'term':tf-idf}, 'docName': {'term':tf-idf}}

        startTime = datetime.datetime.now()
        result_clusters = []
        # For each document,
        #   1. do tokenization
        #   2. update document name list
        #   3. update TF-iDF matrix using the tokens
        for docName in glob.glob(path + '*.html'):
            #   1. do tokenization
            f = codecs.open(docName, 'r')
            tokens = self.tokenize(f.read())
            f.close()
            
            #   2. update document name list
            docName = docName[docName.find('\\')+1: ]
            self._docName.append(docName)

            #   3. update TF data with docIndex and the tokens
            self.__update_TF_Data__(docName, tokens)

        # Transform TF Matrix into TF-iDF Matrix
        self.__compute_TF_iDF_Data__()

        # Computing k-clusters using TF-iDF matrix information and Euclidean Distance
        minRSS, result_clusters = self.__computeClusters_kMean__(k, len(self._docName)*2)
        
        endTime = datetime.datetime.now()
        print("Execution Time: " + str(endTime - startTime))
        print("Min RSS: " + str(minRSS))
        return result_clusters

    def __update_TF_Data__(self, docName, tokens):

        if docName not in self._TF_data:
            self._TF_data[docName] = {}

        data = self._TF_data[docName]

        for token in tokens:
            if token in data:
                data[token] += 1
            else:
                data[token] = 1
        return 0
        
    def __compute_TF_iDF_Data__(self):
        # math.log10(X)
        ## For each term t in current document ##
        # TF(t) = 0,                    if count(t) = 0,
        # TF(t) = 1 + log10(count(t))   otherwise
        # ---------------------------------------------------
        # N = Total number of documnets
        # DF(t) = the number of documents that t occurs
        # iDF(t) = log10(N / DF(t))
        # ---------------------------------------------------
        # TF-iDF(t) = TF-weight * DF-weight = TF(t) * iDF(t)

        N = len(self._TF_data)

        for docName, termData in self._TF_data.items():
            self._TF_iDF_data[docName] = {}

            for term, value in termData.items():
                tf_value = 1 + math.log10(value)

                df = 0
                for tmpDocName, tmpTermData in self._TF_data.items():
                    if term in tmpTermData:
                        df += 1
                idf_value = math.log10(N / df)
                
                self._TF_iDF_data[docName][term] = tf_value * idf_value

            # print(self._TF_data[docName])
            # input('pause1')
            # print(self._TF_iDF_data[docName])
            # input('pause2')


        return 0

    def __computeClusters_kMean__(self, k, repeatCalculationAmount=1):
        if k > len(self._docName):
            print(k)
            print(len(self._docName))
            print("Error: cluster num is larger than doc num.")
            return -1, []

        total_RandomList = []
        bestCluster = {}
        minRSS = sys.maxsize
        for repeatCount in range(repeatCalculationAmount):
            # print("Restart Count: " + str(repeatCount+1))

            # a. random choose k document as initial centroids
            centroidSet = {}
            randomList = []
            while True:
                randomList = random.sample(range(len(self._docName)), k)
                randomList.sort()
                if randomList not in total_RandomList:
                    total_RandomList.append(randomList)
                    break

            for clusterIndex, docIndex in enumerate(randomList):
                centroidSet[clusterIndex] = self._TF_iDF_data[self._docName[docIndex]]

            # b. cluster convergence
            preCluster = {}
            curCluster = {}
            for clusterIndex, docIndex in enumerate(randomList):
                preCluster[clusterIndex] = [self._docName[docIndex]]
                curCluster[clusterIndex] = []

            clusteringSteps = 0
            while True:

                clusteringSteps += 1
                # b-1 for each document, join nearest centroid using Euclidean Distance
                for docName, docData in self._TF_iDF_data.items():
                    minDis = sys.maxsize
                    nearestClusterIndex = 0
                    for clusterIndex, centroid in centroidSet.items():
                        dis = self.__computeEuclideanDistance__(docData, centroid)
                        if dis <= minDis:
                            minDis = dis
                            nearestClusterIndex = clusterIndex
                    
                    if docName not in curCluster[nearestClusterIndex]:
                        curCluster[nearestClusterIndex].append(docName)

                # b-2. update centroid using curCluster
                centroidSet = self.__computeCentroid__(curCluster)

                # b-3. check if current cluster dataset is the same as previous cluster dataset
                if self.__isClusterConverge__(preCluster, curCluster):
                    break
                else:
                    preCluster = copy.deepcopy(curCluster)
                    for clusterIndex in curCluster.keys():
                        curCluster[clusterIndex] = []
            
            # c. update the bestCluster and related RSS value (minRSS)
            curRSS = self.__computeRSS__(centroidSet, curCluster)
            # print("Cur RSS: " + str(curRSS) + '\n')
            if curRSS < minRSS:
                minRSS = curRSS
                bestCluster = copy.deepcopy(curCluster)


        bestCluster_List = []
        for clusterIndex, cluster in bestCluster.items():
            bestCluster_List.append(bestCluster[clusterIndex])

        # print('minRSS: ' + str(minRSS))
        return minRSS, bestCluster_List

    def __computeEuclideanDistance__(self, dictA, dictB):
        result = 0.0

        uniqueKeyList = list(set().union(dictA.keys(), dictB.keys()))
  
        for key in uniqueKeyList:
            singleResult = 0.0
            if key in dictA:
                singleResult = dictA[key]
            if key in dictB:
                singleResult -= dictB[key]
            result += math.pow(singleResult, 2)

        result = math.sqrt(result)
        return result

    def __computeCentroid__(self, curCluster):
        centroidSet = {}
        for clusterIndex, cluster in curCluster.items():
            N = len(cluster)
            curCentroid = {}

            uniqueKeyList = []
            for docName in cluster:
                uniqueKeyList = list(set().union(uniqueKeyList, self._TF_iDF_data[docName].keys()))
            
            for key in uniqueKeyList:
                curCentroid[key] = 0
                for docName in cluster:
                    if key in self._TF_iDF_data[docName]:
                        curCentroid[key] += self._TF_iDF_data[docName][key]
                curCentroid[key] /= N

            centroidSet[clusterIndex] = curCentroid    
        return centroidSet

    def __isClusterConverge__(self, preCluster, curCluster):
        
        preCluster_InList = []
        for clusterIndex, cluster in preCluster.items():
            preCluster_InList.append(cluster)
        
        curCluster_InList = []
        for clusterIndex, cluster in curCluster.items():
            curCluster_InList.append(cluster)

        for cluster in preCluster_InList:
            cluster.sort()
        list.sort(preCluster_InList, key = lambda x : x[0])
        for cluster in curCluster_InList:
            cluster.sort()
        list.sort(curCluster_InList, key = lambda x : x[0])

        if len(preCluster_InList) != len(curCluster_InList):
            return False

        for a , b in zip(preCluster_InList, curCluster_InList):
            if set(a) != set(b):
                    return False
            
        return True

    def __computeRSS__(self, centroidSet, curCluster):
        result = 0.0
        for clusterIndex, centroid in centroidSet.items():
            for docName in curCluster[clusterIndex]:
                result += self.__computeEuclideanDistance__(centroid, self._TF_iDF_data[docName])
        return result

# now, we'll define our main function which actually starts the clusterer
def main(args):
    print(student)
    clustering = Clustering()
    print("test 10 documents")
    print(clustering.consume_dir('test10/', 5))
    print("test 50 documents")
    print(clustering.consume_dir('test50/', 5))

# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)