"""
  SVM (Support Vector Machine) BIBFRAME classifiers
"""
__author__ = "Jeremy Nelson"

import os
import pymarc
import random
import re
import redis

from numpy import float, mat, multiply, shape, zeros
from work_classifer import WorkClassifier, WorkClassifierError
from stopwords import STOPWORDS


class WorkClassifier(WorkClassifier):

    def __init__(self, **kwargs):
        super(WorkClassifier, self).__init__(**kwargs)
        self.work_name = kwargs.get('name', None)
        self.data_matrix, self.label_matrix = [], []


    def clip_alpha(self, aj, H, L):
        if aj > H:
            aj = H
        if L > aj:
            aj = L
        return aj      

    def load_training_marc(self, marc_filename):
        marc_reader = pymarc.MARCReader(open(marc_filename,
                                             'rb'))

    def select_j_rand(self, i, m):
        j=i
        while (j==i):
            j = int(random.uniform(0, m))
        return j

    def smo_simple(self, 
                   data_matix_in, 
                   class_labels,
                   C,
                   toler,
                   max_iter):
        data_matrix = mat(data_matix_in)
        label_matrix = mat(class_labels)
        b = 0
        m, n = shape(data_matrix)
        alphas = mat(zeros((m, 1)))
        iter_counter = 0
        while(iter_counter < max_iter):
            alpha_pairs_changed = 0
            for i in range(m):
                fXi = float(multiply(alphas, label_matrix).T*\
                           (data_matrix*data_matrix[i,:].T)) + b
                Ei = fXi - float(label_matrix[i])
                if ((label_matrix[i]*Ei < -toler) and (alphas[i] < C)) or\
                   ((label_matrix[i]*Ei > toler) and (alphas[i] > 0)):
                    j = self.select_j_rand(i, m)
                    fXj = float(multiply(alphas, label_matrix).T*\
                               (data_matrix*data_matrix[j,:].T)) + b
                    Ej = fXj - float(label_matrix[j])
                    alphaIold = alphas[i].copy()
                    alphaJold = alphas[j].copy()
                    if (label_matrix[i] != label_matrix[j]):
                        L = max(0, alphas[j] - alphas[i])
                        H = min(C, C + alphas[j] - alphas[i])
                    else:
                        L = max(0, alphas[j] + alphas[i] - C )
                        H = min(C, alphas[j] + alphas[i])
                    if L == H:
                        print("L==H")
                        continue
                    eta = 2.0 * data_matrix[i:]*data_matrix[j:].T - \
                          data_matrix[i,:]*data_matrix[j,:].T - \
                          data_matrix[j,:]*data_matrix[j,:].T
                    if eta >= 0:
                        print("eta>=0")
                        continue
                    alphas[j] -= label_matrix[j]*(Ei - Ej)/eta
                    alphas[j] = self.clip_alpha(alphas[j], H, L)
                    if (abs(alphas[i] - alphaJold) < 0.00001):
                        print("j not moving enough")
                        continue
                    alphas[i] += label_matrix[j]*label_matrix[i]*\
                                 (alphaJold = alphas[j])
                    b1 = b - Ei - label_matrix[i]*(alphas[i]-alphaIold)*\
                         data_matrix[i,:]*data_matrix[i,:].T - \
                         label_matrix[j]*(alphas[j]-alphaJold)*\
                         data_matrix[i,:]*data_matrix[j,:].T 

