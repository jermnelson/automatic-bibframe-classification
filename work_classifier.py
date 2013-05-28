"""Base Class for Machine Learning Research on BIBFRAME classification

WorkClassifier should be extended by implementing child classes

"""
__author__ = "Jeremy Nelson"

import redis

class WorkClassifierError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self, value):
        return repr(self.value)

class WorkClassifier(object):

    def __init__(self, **kwargs):
        self.work_name = kwargs.get('name', None)
        self.datastore = kwargs.get('datastore',
                                    redis.StrictRedis())
        
    def __classify__(self, tokens):
        """Method should be overridden by implementing child classes

        Parameters:
        tokens -- List of lowercase tokens
        """
        pass
    
    def __tokenize_marc21__(self, marc_record):
        """Method tokenizes MARC21 record, 

        Should be overridden by be overridden by implementing child classes
        
        Parameters:
        marc_record -- MARC21 Record
        """
        pass
    
    def classify_marc_record(self, marc_record):
        """Method classifies a single MARC21 record

        Should be overridden by be overridden by implementing child classes
       
        Parameters:
        marc_record -- MARC21 Record
        """
        pass
        

    def load_training_marc(self, marc_filename, marc_labels):
        """Method loads a training set of MARC records for a Creative Work

        Should be overridden by be overridden by implementing child classes
        
        Parameters:
        marc_filename -- Full path to marc filename
        marc_labels -- A list of booleans, True is Good, False is Bad
        """
        pass
