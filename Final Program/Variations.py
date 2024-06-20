# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 15:55:19 2024

@author: beaun
"""

import random
from Random_Configuration import set_seed
set_seed()



""" PROGRESSION VARIATIONS """

"""
Replaces a random sequence of chords / notes between the 2nd to 2nd last with their scale relative.
This creates a turn-around, where it starts in major/minor,
moves to the opposite and returns.
"""
def turn_around(progression, scale, length = None):
    
    if len(progression) < 3:
        return progression
    
    # Set length of turn around
    if length is None:
        length = random.randint(1, len(progression) - 2)
    
    # Set start of turnaround
    start = random.randint(1, len(progression) - 1 - length)
            
    # Swap chords / notes with relative
    turn_around = progression.copy()
    for i in range(start, start + length):
        turn_around[i] = scale.relative(progression[i])
    
    return turn_around


  
"""
Replaces a random set of chords / notes in a progression with its scale relative.
If amount is not given, picks at least 1 and at most half of the progression
"""
def relative_variation(progression, scale, amount = None):
    
    # If the progression is too short or the amount is too high
    if len(progression) < 2 or len(progression) < amount:
        return progression
    
    # Pick amount if none is given
    if amount is None:
        amount = random.randint(1, int(len(progression) / 2))
    
    # Pick 2 random chords / notes to switch
    relative = list(range(len(progression)))
    random.shuffle(relative)
    relative = relative[amount:]
            
    # swap chord / note with relative
    turn_around = progression.copy()
    for i in relative:
        turn_around[i] = scale.relative(progression[i])
    
    return progression



"""
Swaps each chord / note with its relative chord / note.
"""
def relative_progression(progression, scale):
    return [scale.relative(chord) for chord in progression]



""" RHYTHM VARIATIONS """

"""
Choose a chord / note in the rhythm and cut it into 2 parts
"""
def split_rhythm(rhythm):
    
    # Find the chords / notes that are at least 4 long
    contenders = []
    for i in range(len(rhythm)):
        if rhythm[i] > 3:
            contenders.append(i)
    
    # If there is no such chord / note, return the original
    if len(contenders) == 0:
        return rhythm
    
    # Copy rhythm so it doesn't overwrite the original
    rhythm = rhythm.copy()
    
    # Pick a chord
    i = random.choice(contenders)
    
    # Pick a slice
    options = [2, 3, 4, 6]
    cut = random.choice(options)
    while cut + 2 > rhythm[i]:
        cut = random.choice(options)
        
    # Cut chord
    rhythm.insert(i + 1, cut)
    rhythm[i] -= cut
    
    return rhythm



"""
Pick 2 random adjecent chords / notes in the rhythm and join them
"""
def join_rhythm(rhythm):
    
    # If there's nothing to join
    if len(rhythm) < 2:
        return rhythm
    
    # Copy rhythm so it doesn't overwrite the original
    rhythm = rhythm.copy()
    
    # Pick a random chord / note pair to join
    i = random.choice(range(len(rhythm) - 1))
    
    # Pop the first
    length = rhythm.pop(i)
    
    # Join it with the other
    rhythm[i] += length
    
    return rhythm



"""
Pick 2 random adjecent chords / notes in the rhythm,
extend / shorten the first and adjust the other accordingly
"""
def shift_rhythm(rhythm):
    
    # If there's nothing to swap
    if len(rhythm) < 2:
        return rhythm
    
    # Copy rhythm so it doesn't overwrite the original
    rhythm = rhythm.copy()
    
    # Find suitable chord / note pair
    contenders = []
    for i in range(len(rhythm) - 1):
        if rhythm[i] + rhythm[i + 1] > 4:
            contenders.append(i)
            
    # If there is no such chord / note pair, return the original
    if len(contenders) == 0:
        return rhythm
            
    # Pick a pair
    i = random.choice(contenders)
    
    # Determine and pick a possible shift
    options = range(-(rhythm[i] - 2), rhythm[i + 1] - 2 + 1)
    shift = random.choice(options)
    
    # Shift the split to the left or right
    rhythm[i] += shift
    rhythm[i + 1] -= shift
    
    return rhythm