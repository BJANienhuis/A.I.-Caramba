# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:55:21 2024

@author: beaun
"""



"""
This function takes 2 chords and applies chord inversions until they are 'optimal' in comparison.
Optimal means that there is as little distance between the chords as possible.
Distance in this case is the difference between the lowest and highest notes of both chords.
"""
def invert(c1, c2):
    
    # Grab lowest and highest note of each chord
    l1, h1, l2, h2 = c1[0], c1[-1], c2[0], c2[-1]
    
    
    # If the second chord is higher than the first
    if l1 + h1 < l2 + h2:
        
        # Calculate distance and first inversion
        d = distance(c1, c2)
        c2_down = inv_down(c2)
        d_new = distance(c1, c2_down)
        
        # Keep applying chord inversions until the distance is optimal
        while d > d_new:
            d = d_new
            c2 = c2_down
            c2_down = inv_down(c2)
            d_new = distance(c1, c2_down)
                
        return c2
    
    # If the second chord is lower than the first    
    elif l1 + h1 > l2 + h2:
        
        # Calculate distance and first inversion
        d = distance(c1, c2)
        c2_up = inv_up(c2)
        d_new = distance(c1, c2_up)
    
        # Keep applying chord inversions until the distance is optimal
        while d > d_new:
            d = d_new 
            c2 = c2_up
            c2_up = inv_up(c2)
            d_new = distance(c1, c2_up)
                
        return c2
        
    # In this case chord inversion won't help
    else:
        return c2
    
    
    
"""
Takes a chord progression and inverts each chord based on the previous
"""
def invert_progression(progression: list):
    # Create list of new progression
    invertedProgression = [progression[0]]
    
    # For each following chord, invert it according to the previous, and add it
    for chord in progression[1:]:
        previous = invertedProgression[-1]
        inversion = invert(previous, chord)
        invertedProgression.append(inversion)
    
    return invertedProgression



"""
Takes a chord progression and inverts each chord based on the first
"""
def invert_progression_2(progression: list):
    # Create list of new progression
    invertedProgression = [progression[0]]
    
    # For each following chord, invert it according to the first, and add it
    for chord in progression[1:]:
        inversion = invert(invertedProgression[0], chord)
        invertedProgression.append(inversion)
    
    return invertedProgression



"""
Returns sum of the distance between:
    the lowest note of 2 chords
    the highest note of 2 chords 
"""
def distance(c1, c2):
    l1, h1, l2, h2 = c1[0], c1[-1], c2[0], c2[-1]
    return abs(l1 - l2) + abs(h1 - h2)



"""
Grabs the highest note of the chord and moves it (in octaves) below the lowest note
"""
def inv_down(c):
    c = c.copy()
    # Take highest note
    h = c.pop()
    # Decrease by octaves until it is below the lowest note
    while h > c[0]:
        h -= 12
    # Add at start
    c.insert(0, h)
    return c



"""
Grabs the lowest note of the chord and moves it (in octaves) above the highest note
"""
def inv_up(c):
    c = c.copy()
    # Take lowest note
    l = c.pop(0)
    # Increase by octaves until it is above the highest note
    while l < c[-1]:
        l += 12
    # Add at end
    c.append(l)
    return c