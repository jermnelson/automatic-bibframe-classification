"""
 jython utilities for Jeremy Nelson 
"""
__author__ = "Jeremy Nelson"
import datetime
import json
import os
import random
import sys
sys.path.append(os.path.join("lib",
                             "marc4j.jar"))
import java.io.FileInputStream as FileInputStream
import java.io.FileOutputStream as FileOutputStream
import org.marc4j as marc4j

DATA_ROOT = os.path.split(os.getcwd())[0]
CARL_STATS = json.load(open('alliance-stats.json', 'rb'))
CARL_POSITIONS = {}
for key in CARL_STATS.keys():
    if type(CARL_STATS[key]) == dict:
        CARL_POSITIONS[(CARL_STATS[key]['start'],
                        CARL_STATS[key]['end'])] = {'filename':key, 
                                                    'training-recs':[],
                                                    'testing-recs':[]}

SORTED_POSITIONS = sorted(CARL_POSITIONS.keys())

def get_range(value, rec_range):
    row = rec_range[0]
    if row[1] >= value and value >= row[0]:
        return row
    else:
        return get_range(value, rec_range[1:])

def GenerateAllianceSets():
    start_time = datetime.datetime.utcnow()
    print("Starting generation of Alliance Training and Testing Sets at {0}".format(start_time.isoformat()))
    training_mrc = marc4j.MarcStreamWriter(
        FileOutputStream(os.path.join("Alliance",
                                      "carl-training.mrc")))
    training_mrc.setConverter(marc4j.converter.impl.AnselToUnicode())
    testing_mrc = marc4j.MarcStreamWriter(
        FileOutputStream(os.path.join("Alliance",
                                      "carl-testing.mrc")))
    testing_mrc.setConverter(marc4j.converter.impl.AnselToUnicode())
    training_pos = []
    print("Generating random record positions")
    for i in xrange(1, 20000):
        rand_int = random.randint(1, int(CARL_STATS.get('total')))
        range_key = get_range(rand_int, SORTED_POSITIONS)
        CARL_POSITIONS[range_key]['training-recs'].append(rand_int)
        training_pos.append(rand_int)
        while 1:
            rand_int2 = random.randint(1, int(CARL_STATS.get('total')))
            if training_pos.count(rand_int2) < 1:
                range_key = get_range(rand_int2, SORTED_POSITIONS)
                CARL_POSITIONS[range_key]['testing-recs'].append(rand_int2)
                break
    print("Finished random position generation, elapsed time={0}".format((datetime.datetime.utcnow() - start_time).seconds / 60.0))
    for key, row in CARL_POSITIONS.iteritems():
        print("\nStarting retrival of {0} records from {1}".format((len(row.get('training-recs')) + len(row.get('testing-recs'))),
                                                                   row.get('filename')))
        print("Elapsed time={0}min".format((datetime.datetime.utcnow() - start_time).seconds / 60.0))
        collection_file = FileInputStream(os.path.join(DATA_ROOT,
                                                       "Coalliance-Catalog",
                                                       row['filename']))
        collection_reader = marc4j.MarcStreamReader(collection_file)
        offset = key[0]
        counter = 0
        while collection_reader.hasNext():
            counter += 1
            record = collection_reader.next()
            if row.get('training-recs').count(counter + offset) > 0:
                training_mrc.write(record)
            if row.get('testing-recs').count(counter + offset) > 0:
                testing_mrc.write(record)
            if not counter%100:
                sys.stderr.write(".")
            if not counter%1000:
                sys.stderr.write("{0}".format(counter))

    training_mrc.close()
    testing_mrc.close()
    end_time = datetime.datetime.utcnow()
    print("Finished generation of CARL sets at {0}".format(end_time.isoformat()))
    print("Total time is {0} minutes".format((end_time-start_time).seconds / 60.0))


def get_carl_marc_record(position):
    previous_value = 0
    marc_file = None
    for number in SORTED_POSITIONS:
        if previous_value <= position and number > position:
            if CARL_POSITIONS.has_key(number):
                marc_file = CARL_POSITIONS[number]
                break
        previous_value = number
    if marc_file is None:
         print("{0} not found in MARC records".format(position))
         return None
#        raise ValueError("{0} not found in MARC records".format(position))
    offset = position - CARL_STATS[marc_file].get('start')
    collection_file = FileInputStream(os.path.join(DATA_ROOT,
                                                   "Coalliance-Catalog",
                                                   marc_file))
    collection_reader = marc4j.MarcStreamReader(collection_file)
    counter = 0
    while collection_reader.hasNext():
        counter += 1
        record = collection_reader.next()
        if counter == offset:
            return record

    

def SlowGenerateAllianceSets():
    start_time = datetime.datetime.utcnow()
    print("Starting generation of Alliance Training and Testing Sets at {0}".format(start_time.isoformat()))
    training_mrc = marc4j.MarcStreamWriter(
        FileOutputStream(os.path.join("Alliance",
                                      "carl-training.mrc")))
    training_mrc.setConverter(marc4j.converter.impl.AnselToUnicode())
    testing_mrc = marc4j.MarcStreamWriter(
        FileOutputStream(os.path.join("Alliance",
                                      "carl-testing.mrc")))
    training_pos, testing_pos = [], []
    print("Creating random positions")
    for i in xrange(1, 20000):
        rand_int = random.randint(1, int(CARL_STATS.get('total')))
        training_pos.append(rand_int)
        while 1:
            rand_int2 = random.randint(1, int(CARL_STATS.get('total')))
            if training_pos.count(rand_int2) < 1:
                testing_pos.append(rand_int2)
                break
    print("Retrieve MARC records for Training Set")
    for i, position in enumerate(sorted(training_pos)):
        record = get_carl_marc_record(position)
        if record is not None:
            training_mrc.write(record)
        if not i%100:
            sys.stderr.write(".")
        if not i%1000:
            sys.stderr.write("{0}".format(i))
    training_mrc.close()
    print("Retrieve MARC records for Testing Set")
    for i, position in enumerate(sorted(testing_pos)):
        record = get_carl_marc_record(position)
        if record is not None:
            testing_mrc.write(record)
        if not i%100:
            sys.stderr.write(".")
        if not i%1000:
            sys.stderr.write("{0}".format(i))
    testing_mrc.close()
    end_time = datetime.datetime.utcnow()
    print("Finished generation of CARL sets at {0}".format(end_time.isoformat()))
    print("Total time is {0} minutes".format((end_time-start_time).seconds / 60.0))

def GenerateColoradoCollegeSets(marc_file, max_recs=984751):
    start_time = datetime.datetime.utcnow()
    print("Start GenerateColoradoCollegeSets at {0}".format(start_time.isoformat()))

    collection_file = FileInputStream(os.path.join(DATA_ROOT,
                                                   "TIGER-MARC21",
                                                   marc_file))
    collection_reader = marc4j.MarcStreamReader(collection_file)
    training_mrc = marc4j.MarcStreamWriter(
        FileOutputStream(os.path.join("ColoradoCollege",
                                      "cc-training.mrc")))
    training_mrc.setConverter(marc4j.converter.impl.AnselToUnicode())
    testing_mrc = marc4j.MarcStreamWriter(
        FileOutputStream(os.path.join("ColoradoCollege",
                                      "cc-testing.mrc")))
    random_rec_positions = []
    print("Generating random sequences")
    for i in xrange(1, 20000):
        random_rec_positions.append(random.randint(1, max_recs))
    training_pos = list(set(random_rec_positions))
    random_rec_positions = []
    for i in xrange(1, 20000):
        while 1:
           rand_int = random.randint(1, max_recs)
           if training_pos.count(rand_int) < 1:
               random_rec_positions.append(rand_int)
               break
    testing_pos = list(set(random_rec_positions))
    counter = 0
    print("Iterating through {0}".format(marc_file))
    while collection_reader.hasNext():
        counter += 1
        record = collection_reader.next()
        if training_pos.count(counter) > 0:
            try:
                training_mrc.write(record)
            except:
                print("Failed to write training {0} {1}".format(row.title().encode('utf-8', 'ignore'), 
                                                                counter))
        if testing_pos.count(counter) > 0:
            try:
                testing_mrc.write(record)
            except:
                print("Failed to write testing {0} {1}".format(row.title().encode('utf-8', 'ignore'),
                                                               counter))
        if not counter%100:
            sys.stderr.write(".")
        if not counter%1000:
            sys.stderr.write(" {0} ".format(counter))
    training_mrc.close()
    testing_mrc.close()
    end_date = datetime.datetime.utcnow()
    print("Finished generating Colorado College training and testing sets at {0}".format(end_date.isoformat()))
    print("Total time {0} minutes".format((end_date - start_time).seconds / 60.0))
