# -*- coding: utf-8 -*-
"""
Created on Sat May 25 16:12:08 2024

@author: beaun
"""

""" VALUES """

# Ties a value to the 'importance' of a chord / note in scale
value = {
    1: 4,
    2: 2,
    3: 2,
    4: 3,
    5: 3,
    6: 2,
    7: 1}



""" FUNCTIONS """

"""
Split a rhythm into 2 halves. These are picked in such a way
that the halves are as close together in length as possible.
"""
def divide_rhythm(rhythm):
    
    mark = sum(rhythm) / 2
    
    # Keep adding chords until it passes the halfway mark
    # (in terms of summed length)
    i = 1
    while sum(rhythm[:i]) < mark:
        i += 1
        
    # In case 1 chord less divides the halves better, adjust i
    if abs(mark - sum(rhythm[:i-1])) < abs(mark - sum(rhythm[:i])):
        i -= 1
    
    return i



"""
Split a progression into 2 halves. These are picked in such a way
that the second half starts with a stronger chord / note
"""    
def divide_progression(progression):
    
    # If the progression is divisible by 2
    if len(progression) % 2 == 0:
        return int(len(progression) / 2)
    
    # If not
    else:
        i = int(len(progression) / 2)
        
        # Choose the half that starts with a 'stronger' chord
        if value.get(progression[i - 1]) < value.get(progression[i]):
            i += 1
            
        return i
        


"""
Keep splitting both the progression and rhythm into halves until there is 1 chord,
use that to 'fill in' the matching rhythm. Return a chord progression
that matches the length of the rhythm.
"""
def combine(progression, rhythm):
    
    # Base case
    if len(progression) == 1:
        return [progression[0] for _ in rhythm]
    
    # Split Chords
    p = divide_progression(progression)
    
    # Split Rhythm
    r = divide_rhythm(rhythm)
    
    return combine(progression[:p], rhythm[:r]) + combine(progression[p:], rhythm[r:])