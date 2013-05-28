__author__ = "Jeremy Nelson"
import os
import redis
import unittest
from naive_bayes import CustomWorkClassifier, RedisBayesWorkClassifier
from numpy import array

from conf import TEST_REDIS



class TestMobyDick(unittest.TestCase):

    def setUp(self):
        self.classifier = RedisBayesWorkClassifier(
            name="Moby Dick",
            datastore=TEST_REDIS)
        self.labels = [False, False, False, True, True, False, True, False,
                       True, False,True, False, False, False, True, True, True, 
                       True, True, False, False, False]
        self.classifier.load_training_marc(os.path.join('ColoradoCollege',
                                                        'moby-dick.mrc'),
                                           self.labels)

    def test_init(self):
        self.assert_(self.classifier is not None)
        self.assertEquals(len(self.labels), 22) 

    def test_classify(self):
        false_tokens = ["pride prejudice jane austen",
                        "infinite jest david foster wallace"]
        true_tokens = ["moby dick hermin melville 1841 1891",
                       "moby dick herman melville"]
        for tokens in false_tokens:
            print("False: {0} {1}".format(tokens, self.classifier.__classify__(tokens)))
            self.assert_(not self.classifier.__classify__(tokens))
        for tokens in true_tokens:
            #print("True {0} {1}".format(tokens, self.classifier.__classify__(tokens)))
            self.assert_(self.classifier.__classify__(tokens))

     
    def tearDown(self):
        TEST_REDIS.flushdb()



class TestRedisBayesWorkClassifierPrideAndPrejudice(unittest.TestCase):

    def setUp(self):
        self.classifier = RedisBayesWorkClassifier(
            name="Pride and Prejudice",
            datastore=TEST_REDIS)
        self.labels = [False, # b1629290
                       False, # b2006265
                       True, # b1276421
                       True, # b1313597
                       True, # b1329008
                       True, # b1143215
                       True, # b1177629
                       False, # b1224585
                       True, # b1009861
                       True, # b1605863
                       True, # b1685471
                       False, # b1724262
                       False, # b1724269
                       False, # b1285281
                       False, # b1629141
                       False, # b1636638
                       False, # b1636639
                       False, # b1285281
                       True, # b2033293
                       False, # b1724269
                       False, # b1724262
                       False, # b1629141
                       False, # b1238652
                       False, # b1433978
                       False, # b1628582
                       False, # b1022859
                       False, # b1773251
                       False, # b2089950
                       False, # b1146944
                       False] # b1675906
        self.classifier.load_training_marc(
            os.path.join('ColoradoCollege',
                         'pride-and-prejudice.mrc'),
            self.labels)

    def test_init(self):
        self.assert_(self.classifier is not None)
        self.assertEquals(len(self.labels), 30)

        
    def test_classify_(self):
        false_tokens = ["infinite jest david foster wallace",
                        "jane austen sense sensibility"]
        true_tokens = ["pride prejudice jane austen",
                       "pride prejudice jane austen 1775 1817"]
        for tokens in false_tokens:
            print("{0} is {1}".format(tokens,
                                      self.classifier.__classify__(tokens)))
            self.assert_(not self.classifier.__classify__(tokens))
        for tokens in true_tokens:
            self.assert_(self.classifier.__classify__(tokens))
 
    def tearDown(self):
        TEST_REDIS.flushdb()


class TestCustomWorkClassifierClassifierPrideAndPrejudice(unittest.TestCase):

    def setUp(self):
        self.classifier = CustomWorkClassifier(name="Pride and Prejudice",
                                               datastore=TEST_REDIS,
                                               simple=True)
        self.labels = [0, # b1629290
                       0,
                       1,
                       1,
                       1,
                       1,
                       1,
                       0,
                       1,
                       1,
                       1,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       1,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0] 

    def test_init(self):
        self.assert_(self.classifier is not None)
        self.assertEquals(len(self.labels), 30)

    def test_load_training_marc(self):
        self.classifier.load_training_marc(
            os.path.join('ColoradoCollege',
                         'pride-and-prejudice.mrc'))
        self.assertEquals(len(self.classifier.training_data),
                          30)

    def test_generate_training_labels(self):
        labels = 30*[0]
        self.classifier.load_training_marc(
            os.path.join('ColoradoCollege',
                         'pride-and-prejudice.mrc'))
        self.classifier.generate_training_labels(labels=labels)
        self.assertEquals(labels, 
                          self.classifier.training_labels)

    def test_generate_training_vocabulary(self):
        self.classifier.load_training_marc(
            os.path.join('ColoradoCollege',
                         'pride-and-prejudice.mrc'))
        self.classifier.generate_training_labels(labels=self.labels)
        self.classifier.generate_training_vocabulary()
        self.assertEquals(self.classifier.training_vocabulary, 
                          set(['affair', 'bebris', 'helen', 'matters', 
                               '1817', 'prejudice', 'jane', 'impressions', 
                               'pride', 'crawford', '1958', 'first', 
                               'sentimental', 'carrie', '1883', 'prejudiceor', 
                                'mansfield', '1775', 'austen', 'prejudice', 
                               'comedy', 'jerome', 'mystery', 'emma',
                               'annotated', 'edition', 'darcy', 'acknowledged',
                               'mr', 'park', 'revisited', 'mrs', 'prescience',
                               'suspense', 'truth', 'sense', 'sensibility',
                               'universally']))

    def test_tokens2vectors(self):
        self.classifier.load_training_marc(
            os.path.join('ColoradoCollege',
                         'pride-and-prejudice.mrc'))
        self.classifier.generate_training_labels(labels=self.labels)
        self.classifier.generate_training_vocabulary()
        self.assertEquals(self.classifier.tokens2vectors(['austen', 
                                                          'first', 
                                                          'matters']),
                         [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0,
                          0, 0, 0, 0,  0, 0, 0, 0, 0, 1])


    def test_generate_training_matrix(self):
        self.classifier.load_training_marc(
            os.path.join('ColoradoCollege',
                         'pride-and-prejudice.mrc'))
        self.classifier.generate_training_labels(labels=self.labels)
        self.classifier.generate_training_vocabulary()
        self.classifier.generate_training_matrix()
        self.assertEquals(self.classifier.training_matrix[0][6],
                          1)  
        
         
    def test_train_naive_bayes(self):
        self.classifier.load_training_marc(
            os.path.join('ColoradoCollege',
                         'pride-and-prejudice.mrc'))
        self.classifier.generate_training_labels(labels=self.labels)
        self.classifier.generate_training_vocabulary()
        self.classifier.generate_training_matrix()
        self.classifier.train_naive_bayes()
        self.assertEquals(self.classifier.pWork, 
                          0.47368421052631576)
        self.assertEquals(self.classifier.p0Vector[0], 0.029411764705882353)
        self.assertEquals(self.classifier.p1Vector[6], 0.16666667)

    def test_classify(self):
        self.classifier.load_training_marc(
            os.path.join('ColoradoCollege',
                         'pride-and-prejudice.mrc'))
        self.classifier.generate_training_labels(labels=self.labels)
        self.classifier.generate_training_vocabulary()
        self.classifier.generate_training_matrix()
        self.classifier.train_naive_bayes()
        self.assertEquals(self.classifier.classify(['jane', 'austen', 
                                                    'pride', 'prejudice']),
                          1)
        self.assertEquals(self.classifier.classify(['jane', 'eyre', 'anne', 'green']),
                          0)
       


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
