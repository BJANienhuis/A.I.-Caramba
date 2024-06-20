# -*- coding: utf-8 -*-
"""
Created on Sun May  5 20:00:18 2024

@author: beaun
"""

""" IMPORTS """

from MIDI_Extractor import collect_paths, read_file, reduce
from Scale import Scale
from Melody_Rhythms import split



""" FUNCTIONS """

"""
Cycle a scale (major & minor) and try to find a satisfying abstraction
"""
def find_abstraction(scale, progression):
    
    # Try both major and minor
    for _ in range(2):
        
        # Cycle the octave
        for _ in range(12):
            
            # Attempt to abstract with the current scale
            abstraction = scale.abstract_progression(progression)
            
            # If an abstraction has been found
            if abstraction and 1 in abstraction:
                
                return abstraction
                
            # If no abstraction has been found
            else:
                
                # Modulate the scale to the next
                scale.modulate(1)
        
        # Flip minor to major or vice versa
        scale.flip_mode()
        
        

"""
Return false if rhythm is not usable. Conditions:
    - Rhythm does not sum to a mutliple of 16
    - Rhythm contains 1's (too fast, doesn't sound good for chords)
"""
def suitable(rhythm):
    
    # Check if rhythm sums to multiple of 16
    if sum(rhythm) % 16 != 0:
        return False
    
    # Check if rhythm contains a 1
    for number in rhythm:
        if number == 1:
            return False
    
    # If none of the filter conditions were met
    return True
      
        
        
"""
Reduce a progression only to its chord changes (remove adjecent duplicates)
"""
def simplify(progression):
    
    simplified = []
    
    for i in range(len(progression)):
        
        # Only add elements if they're the first, or different from the last
        if i == 0 or progression[i] != progression[i - 1]:
            
            simplified.append(progression[i])
    
    return simplified
    


""" COLLECTING FILEPAHTS """

# Directories containing MIDI files
directories = [
    "MIDI/TERROR/OTHER/MIN",
    "MIDI/TERROR/MELO/CHORDS/MIN",
    "MIDI/TITAN/OTHER/MIN",
    "MIDI/TITAN/MELO/CHORDS/MIN",
    "MIDI/TERROR/OTHER/MAJ",
    "MIDI/TITAN/OTHER/MAJ",
    "MIDI/TITAN/MELO/CHORDS/MAJ"
    ]

# Collect paths to files
paths = collect_paths(directories)
    
    
    
""" COLLECTING PROGRESSIONS """

progressions = []

for path in paths:
    
    # Convert to progression
    progression = read_file(path)
    
    # Remove loops
    progression = reduce(progression)
    
    progressions.append(progression)
    
    

""" EXTRACT RHYTHMS """

# Extract rhythms from the chord progressions
rhythms = [[length for (chord, length) in progression] for progression in progressions]

# Reduce rhythms
rhythms = [reduce(rhythm) for rhythm in rhythms]

rhythms_selection = list()

# Remove rhythms that don't add up to a multiple of 16 and remove duplicates
for rhythm in rhythms:
    if suitable(rhythm):

        # Split into chunks that sum to 16
        chunks = split(rhythm)
        
        for rhythm in chunks:
            
            if rhythm not in rhythms_selection:
                rhythms_selection.append(rhythm)



""" ABSTRACT PROGRESSIONS """

# Extract chords from the chord progressions
chord_progressions = [[list(chord) for (chord, length) in progression] for progression in progressions]

# Create scale
scale = Scale('C', 'Minor')

abstract_progressions = []

# Abstract progressions
for progression in chord_progressions:
    
    abstraction = find_abstraction(scale, progression)
    
    # If an abstraction has been found
    if abstraction:
        
        # Simplify progression
        abstraction = simplify(abstraction)
        
        # Remove loops
        abstraction = reduce(abstraction)
        
        abstract_progressions.append(abstraction)



""" WRITE RESULTS TO FILE """

# Write rhythms to file
with open('Patterns/Chords/rhythms (extraction).txt', 'w') as file:
    
    for progression in rhythms_selection:
        
        # Join the elements of the progression list into a string and write it to the file
        file.write(' '.join(map(str, progression)) + '\n')
        
# Write chord progressions to file
with open('Patterns/Chords/progressions (extraction).txt', 'w') as file:
    
    for progression in abstract_progressions:
        
        # Join the elements of the progression list into a string and write it to the file
        file.write(' '.join(map(str, progression)) + '\n')   