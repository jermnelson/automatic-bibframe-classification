"""Base Class for Machine Learning Research on BIBFRAME classification

WorkClassifier should be extended by implementing child classes

"""
__author__ = "Jeremy Nelson"

import os
import re
import redis
from stopwords import STOPWORDS

class WorkClassifierError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class WorkClassifier(object):

    def __init__(self, **kwargs):
        self.work_class = None
        self.work_name = kwargs.get('name', None)
        self.datastore = kwargs.get('datastore',
                                    redis.StrictRedis())
        
    def __classify__(self, tokens):
        """Method should be overridden by implementing child classes

        Parameters:
        tokens -- List of lowercase tokens
        """
        pass

    def __classify_work_class__(self, marc_record):
        "Classifies the work as specific Work class based on BIBFRAME website"
        leader = marc_record.leader
        field007 = marc_record['007']
        field336 = marc_record['336']
        if leader[6] == 'a':
            # Book is the default for Language Material
            self.work_class = 'Book'
        elif leader[6] == 'c':
            self.work_class = 'NotatedMusic'
        elif leader[6] == 'd':
            self.work_class = 'Manuscript'
        elif leader[6] == 'e' or leader[6] == 'f':
            # Cartography is the default
            self.work_class = 'Cartography'
            if leader[6] == 'f':
                self.work_class = 'Manuscript'
            if field007.data[0] == 'a':
                self.work_class = 'Map'
            elif field007.data[0] == 'd':
                self.work_class = 'Globe'
            elif field007.data[0] == 'r':
                self.work_class = 'RemoteSensingImage'
        elif leader[6] == 'g':
            self.work_class = 'MovingImage'
        elif leader[6] == 'i':
            self.work_class = 'NonmusicalAudio'
        elif leader[6] == 'j':
            self.work_class = 'MusicalAudio'
        elif leader[6] == 'k':
            self.work_class = 'StillImage'
        elif leader[6] == 'm':
            self.work_class = 'SoftwareOrMultimedia'
        elif leader[6] == 'p':
            self.work_class = 'MixedMaterial'
        elif leader[6] == 'r':
            self.work_class = 'ThreeDimensionalObject'
        elif leader[6] == 't':
            self.work_class = 'Manuscript'
        if self.work_class is None:
            self.work_class = 'Work'
    
    def __tokenize_marc21__(self, marc_record):
        """Method tokenizes MARC21 record

        Parameters:
        marc_record -- MARC21 Record
        """
        words_re = re.compile(r"(\w+)")
        def __filter_term__(term):
            terms = []
            for word in words_re.findall(term):
                word = word.lower()
                if STOPWORDS.count(word.lower()) < 1:
                    terms.append(word)
            return terms
        tokens = []        
        title = marc_record.title()
        if title is not None:
            tokens.extend(__filter_term__(title))                
        author = marc_record.author()
        if author is not None:
            tokens.extend(__filter_term__(author))
        # Gets subclass of Creative Work classification based on the
        # bibframe.org rules at http://bibframe.org/vocab/Work.html
        self.__classify_work_class__(marc_record)
        tokens.extend(__filter_term__(self.work_class))
        return list(set(tokens))
    
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
