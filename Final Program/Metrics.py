# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 15:37:08 2024

@author: beaun
"""

import math



""" TRANSFORMATION METHODS """



"""
Creates a 'fingerprint' of a set of notes.
This allows notes to be equalled to each other without being on the same octave.
"""
def fingerprint(notes):
    
    # If it is a chord
    if type(notes) == list:
        fingerprint = set()
        
        for note in notes:
            fingerprint.add(note % 12)
            
    # If it is a single note
    else:
        fingerprint = notes % 12
        
    return fingerprint
    


"""
Create a grid similar to the drumgrid, but instead with the fingerprint of the progression
"""
def progression_grid(sequence):
    
    grid = []
    
    # For each set of notes, add their fingerprint [length] times
    for notes, length in sequence:
        
        # For this grid, it doesn't matter if a chord is continuing from a previous sequence
        length = abs(length)
        
        # Calculate fingerprint
        notes = fingerprint(notes)
        
        while length > 0:
            
            # Fill with fingerprints
            grid.append(notes)
            length -= 1
            
    return grid



"""
Converts a rhythm (whole numbers) to sequences of 1 and 0.
(i.e. (4, 4) becomes (1, 0, 0, 0, 1, 0, 0, 0))
"""
def rhythm_grid(rhythm):
    
    grid = []
    
    for length in rhythm:
        
        # If it is a 'new' chord / note
        if length > 0:
            
            # Start with a 1
            grid.append(1)
            length -= 1
            
            # Continue with 0's
            while length > 0:
                grid.append(0)
                length -= 1
            
        # If the note is continuing from another sequence
        else:
            
            # Fill with 0's
            while length < 0:
                grid.append(0)
                length += 1
                
    return grid



""" EVALUATION METHODS """

"""
Takes two sequences (given as 0's and 1's), and returns the number of differing steps.
(Automatically stops when the shortes sequence is exhausted)
"""
def pairwise_difference(s1, s2):
    
    match = zip(s1, s2)
        
    # Count the differences
    differences = 0
    for e1, e2 in match:
        if e1 != e2:
            differences += 1
            
    return differences



"""
Calculates the difference between 2 sequences using the levenshtein distance algorithm
"""
def levenshtein_distance(s1, s2):
    
    # Initialise matrix
    h = len(s1) + 1
    w = len(s2) + 1
    d = [[0 for x in range(w)] for x in range(h)]

    # Initialise first row and column
    for i in range(1, h):
        d[i][0] = i
    for j in range(1, w):
        d[0][j] = j

    # Compute the Levenshtein distance
    for i in range(1, h):
        for j in range(1, w):
            if s1[i - 1] == s2[j - 1]:
                c = 0
            else:
                c = 1
            d[i][j] = min(  d[i - 1][j] + 1,        # Deletion
                            d[i][j - 1] + 1,        # Insertion
                            d[i - 1][j - 1] + c) # Substitution

    # Return the computed distance
    return d[h - 1][w - 1]



"""
Calculate the euclidian distance between 2 tuples
"""
def euclidian_distance(t1, t2, weights = None):
    
    # If only 1 metric is used
    if type(t1) == int and type(t2) == int:
        return abs(t1 - t2)
    
    # If only 1 metric is used and it is matched against an emtpy tuple
    elif type(t1) == int or type(t2) == int:
        return 0
    
    # If no weights were given, make them all 1
    if weights is None:
        weights = [1 for _ in range(len(t1))]
    
    distance = 0
    
    for (e1, e2, w) in zip(t1, t2, weights):
        
        distance += w * (e1 - e2) ** 2 
        
    return math.sqrt(distance)