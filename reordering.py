import numpy as np
import math

dim_palette = 0

def compute_distance_matrix(indexed_image,palette):
    lp = len(palette)
    
    if dim_palette != lp: #initialize palette-related weights only if a different palette is provided
        palette_w = []
        for j in range(lp):
            row = []
            for i in range(lp):
                row.append(float(abs(j-i)))
            palette_w.append(row)

        palette_w = np.asarray(palette_w)
        palette_w = palette_w / (lp-1)
    
    indexed_image = np.asarray(indexed_image)
    length = indexed_image.shape[0] * indexed_image.shape[1]
    raster_scanning = indexed_image.reshape(length)
    
    
    
    co_occurrence_matrix = np.zeros([lp,lp])
    for i in range(2,len(raster_scanning)):
        co_occurrence_matrix[raster_scanning[i-1]][raster_scanning[i]] += 1

    co_occurrence_w_norm = np.zeros([lp,lp])
    
    for i in range(lp):
        for j in range(lp):
            if i != j:
                value = co_occurrence_matrix[i][j] + co_occurrence_matrix[j][i]
                if value != 0:
                    co_occurrence_w_norm[i][j] = 1/value
                    co_occurrence_w_norm[j][i] = 1/value
                else:
                    co_occurrence_w_norm[i][j] = 255
                    co_occurrence_w_norm[j][i] = 255
    
    
    
    distance_matrix = palette_w + co_occurrence_w_norm
    #distance_matrix = co_occurrence_w_norm
    return distance_matrix

def reorder_indexed_image(indexed_image,reodered_palette):
    reodered_palette = np.asarray(reodered_palette)
    reordered_indexed_image = reodered_palette[np.asarray(indexed_image)]
    
    return reordered_indexed_image

def entropy2(labels):
    """ Computes entropy of label distribution. """
    n_labels = float(len(labels))

    if n_labels <= 1:
        return 0

    counts = np.bincount(labels)
    probs = counts / n_labels
    n_classes = np.count_nonzero(probs)

    if n_classes <= 1:
        return 0

    ent = 0.

    # Compute standard entropy.
    for i in probs:
        if i == 0:
            continue
        ent -= i * math.log(float(i), n_classes)

    return ent

def compute_entropy(indexed_image):
    raster = indexed_image.reshape(np.shape(indexed_image)[0]*np.shape(indexed_image)[1])
    
    i = 0.0
    diff = []
    while i < len(raster) - 1:
        diff.append(long(raster[int(i)]) - long(raster[int(i)+1]))
        i += 1
        
    return entropy2(np.asarray(diff)+abs(min(diff))) #this to solve negative numbers




#Simulated Annealing
#from __future__ import print_function
import random
from simanneal import Annealer
class ReindexingProblem(Annealer):

    """Test annealer with a travelling salesman problem.
    """
    
    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, indexed_image):
        self.indexed_image = indexed_image
        super(ReindexingProblem, self).__init__(state)  # important! 

    def move(self):
        """Swaps two cities in the route."""
        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """Calculates the length of the route."""
        self.indexed_image = reorder_indexed_image(self.indexed_image,self.state)
        return compute_entropy(self.indexed_image)
