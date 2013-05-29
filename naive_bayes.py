__author__ = "Jeremy Nelson"

import os
import pymarc
import re
import redis
import redisbayes

from lxml import etree
from numpy import array, float, log, ones, sum, zeros 
from stopwords import STOPWORDS
from work_classifier import WorkClassifier, WorkClassifierError

def load_pg_rdf():
    "Function loads titles/authors into a list for training"
    pg_training_results = next(os.walk(os.path.join("ProjectGutenberg",
                                                    "training")))
    



class RedisBayesWorkClassifier(WorkClassifier):

    def __init__(self, **kwargs):
        super(RedisBayesWorkClassifier, self).__init__(**kwargs)
        self.rb = redisbayes.RedisBayes(redis=self.datastore)
        
    def __classify__(self, tokens):
        """Method classifies a list of tokens based on training

        Parameters:
        tokens -- List of lowercase tokens
        """
        result = self.rb.classify(tokens)
        score = self.rb.score(tokens)
        if result.startswith('good'):
            return True
        elif result.startswith('bad'):
            return False
        else:
            raise WorkClassifierError("Unknown result={0}".format(result))
           

    def classify_marc_record(self, marc_record):
        """Method classifies a single MARC21 record

        Returns Boolean based on the Bayes classifier of the MARC21 
        record by breaking down title and author into tokens
       
        Parameters:
        marc_record -- MARC21 Record
        """
        tokens = self.__tokenize_marc21__(self, marc_record)
        return self.__classify__(tokens)
        

    def load_training_marc(self, marc_filename, marc_labels):
        """Method loads a training set of MARC records for a Creative Work
        
        Parameters:
        marc_filename -- Full path to marc filename
        marc_labels -- A list of booleans, True is Good, False is Bad
        """
        marc_reader = pymarc.MARCReader(open(marc_filename, 'rb'))
        words_re = re.compile(r"(\w+)")
        self.records = []
        for record in marc_reader:
            self.records.append(record)
        if len(self.records) != len(marc_labels):
            error_msg = "Number of records {0} must match MARC Labels {1}".format(
                len(self.records),
                len(marc_labels))
            raise WorkClassifierError(error_msg)
        count = 0
        good_tokens, bad_tokens = [], []
        for record in self.records:
            tokens = self.__tokenize_marc21__(record)
            if marc_labels[count] is True:
                good_tokens.extend(tokens)        
            elif marc_labels[count] is False:
                bad_tokens.extend(tokens)
            else:
                raise WorkClassifierError("Unknown value for rec #{0} {1} {3}".format(
                    count,
                    marc_labels[count],
                    tokens))
            count += 1
        self.rb.train('good', ' '.join(good_tokens))
        self.rb.train('bad', ' '.join(bad_tokens))
     
class CustomWorkClassifier(WorkClassifier):
    """Class based on code snippets originally contained in Peter
    Harrington's Machine Learning in Action, (c) 2012

    """
    def __init__(self, **kwargs):
        super(CustomWorkClassifier, self).__init__(**kwargs)
        self.training_data = list()
        self.training_labels = list()
        self.training_matrix = []
        self.training_vocabulary = set([])
        self.simple = kwargs.get('simple', False)

    def classify(self, token_list):
        """Method classifies a vector of tokens 

        If the probability that the token vector is the Work,
        return 1, otherwise return 0

        Parameters:
        token_list -- A set of tokens to be tested
        """
        token_vector = array(self.tokens2vectors(token_list))
        if self.simple is True:
            p0 = sum(token_vector * self.p0Vector) + self.pWork
            p1 = sum(token_vector * self.p1Vector) + self.pWork
        else:
            p0 = sum(token_vector * self.p0Vector) + log(1.0 - self.pWork)
            p1 = sum(token_vector * self.p1Vector) + log(self.pWork)
        print("""For {0},
p0={1} p1={2},
token_vector={3}
p0Vector={4}
p1Vector={5}
""".format(token_list, 
           p0, 
           p1, 
           token_vector, 
           self.p0Vector,
           self.p1Vector))
        if p1 > p0:
            return 1
        return 0


    def generate_training_labels(self, labels=None):
        """Method generates a set of binary ints for each training data row

        Parameters:
        labels -- Existing set of binary 1 and 0s, default is None
        """
        if labels is not None:
            self.training_labels = labels
        else: # Manually prompt 
            for row in self.training_data:
                is_work = 0
                print(' '.join(row))
                prompt = raw_input(r"Is {0}? (y|n)".format(self.work_name))
                if prompt.lower().startswith('y'):
                    is_work = 1
                self.training_labels.append(is_work)

    def generate_training_matrix(self):
        for row in self.training_data:
            self.training_matrix.append(self.tokens2vectors(row)) 
        
    def generate_training_vocabulary(self):
        "Method generates a vocabulary set for the Work"
        for row in self.training_data:
            self.training_vocabulary= self.training_vocabulary | set(row)

    def load_training_marc(self, marc_filename):
        """Method loads a training set of MARC records for a Creative Work
        
        Parameters:
        marc_filename -- Full path to marc filename
        """
        marc_reader = pymarc.MARCReader(open(marc_filename, 'rb'))
        words_re = re.compile(r"(\w+)")
        for record in marc_reader:
            self.training_data.append(self.__tokenize_marc21__(record))

    def load_training_rdf(self, rdf_location, is_gutenberg=False):
        """Method loads a RDF file into training data

        Parameter:
        rdf_location -- Full to RDF filename
        is_gutenberg -- Process Project Gutenberg Specific RDF format
        """
        rdf_xml = etree.XML(open(rdf_location, 'rb'))
        if is_gutenberg is True:
             pass
        

    def tokens2vectors(self, input_set):
        """Converts a list of tokens to a vector of weights  
        

        Parameters:
        input_set -- a set of word tokens extracted from a single source
        """
        result_vector = [0]*len(self.training_vocabulary)
        vocab_list = list(self.training_vocabulary)
        for token in input_set:
            if token in self.training_vocabulary:
                if self.simple is True:
                    result_vector[vocab_list.index(token)] = 1
                else:
                    result_vector[vocab_list.index(token)] += 1
            else:
                print("{0} not found in training_vocabulary!".format(token))
        return result_vector


    def train_naive_bayes(self):
        "Trains the classifier using Naive Bayes conditional probabilities"
        total = len(self.training_matrix)
        number_tokens = len(self.training_matrix[0])
        self.pWork = sum(self.training_labels)/float(total)
        if self.simple is True:
            p0Number, p1Number = zeros(number_tokens), zeros(number_tokens)
            p0Denominator, p1Denominator = 0.0, 0.0
        else:
            p0Number, p1Number = ones(number_tokens), ones(number_tokens)
            p0Denominator, p1Denominator = 2.0, 2.0        
        for i in range(total):
            if self.training_labels[i] == 1:
                p1Number += self.training_matrix[i]
                p1Denominator += sum(self.training_matrix[i])
            else:
                p0Number += self.training_matrix[i]
                p0Denominator += sum(self.training_matrix[i])
        if self.simple is True:
            self.p0Vector = p0Number / p0Denominator
            self.p1Vector = p1Number / p1Denominator
        else:
            self.p0Vector = log(p0Number / p0Denominator)
            self.p1Vector = log(p1Number / p1Denominator)
        


