__author__ = "Jeremy Nelson"
import os
import pymarc
import redis
import unittest
from conf import TEST_REDIS
from work_classifier import WorkClassifier

class TestWorkClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = WorkClassifier(name="Test",
                                         datastore=TEST_REDIS)
        

    def test_init(self):
        self.assert_(self.classifier)

    def test_tokenize_marc21_one(self):
        marc_record = pymarc.Record()
        marc_record.leader = marc_record.leader[0:6] + 'a' + marc_record.leader[7:]
        marc_record.add_field(
            pymarc.Field(tag='100',
                         indicators=['1', ' '],
                         subfields=['a','Naslund, Sena Jeter.']))
        marc_record.add_field(
            pymarc.Field(tag='245',
                         indicators=['1', '0'],
                         subfields = ['a', "Ahab's wife, or, The star-gazer :",
                                      'b', "a novel /"]))
        
        
        self.assertEquals(
            sorted(self.classifier.__tokenize_marc21__(marc_record)),
            ['ahab',
             'book',
             'gazer',
             'jeter',
             'naslund',
             'novel',
             'sena',
             'star',
             'wife'])

    def test_tokenize_marc21_title_only(self):
        marc_record = pymarc.Record()
        marc_record.add_field(
            pymarc.Field(tag='245',
                         indicators=['1', '0'],
                         subfields = ['a', "Ahab's wife, or, The star-gazer :",
                                      'b', "a novel /"]))
        self.assertEquals(
            self.classifier.__tokenize_marc21__(marc_record),
            ['novel', 'star', 'ahab', 'wife', 'work', 'gazer'])

    

    def tearDown(self):
        TEST_REDIS.flushdb()
        
if __name__ == '__main__':
    unittest.main()
