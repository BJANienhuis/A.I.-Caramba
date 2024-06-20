# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 12:06:38 2024

@author: beaun
"""

""" IMPORTS """

from MIDI_Extractor import collect_paths, read_file, reduce
from Scale import Scale
from Combiner import divide_rhythm



""" COLLECTING FILEPAHTS """

# Directories containing MIDI files
directories = [
    "MIDI/TITAN/MELO/MELO/MAJ",
    "MIDI/TITAN/MELO/MELO/MIN",
    "MIDI/TERROR/MELO/MELO/MIN"
    ]

# Collect paths to files
paths = collect_paths(directories)



""" FUNCTIONS """

"""
Return false if rhythm is not usable. Conditions:
    - Rhythm does not sum to a mutliple of 16
"""
def suitable(rhythm):
    
    # Check if rhythm sums to multiple of 16
    if sum(rhythm) % 16 != 0:
        return False
    
    # If non of the filter conditions were met
    return True


"""
Split a given rhythm into chunks that sum to 16 (if possible)
"""
def split(rhythm):

    # Create temporary list & final output list
    splits = [rhythm]
    output = list()
    
    while len(splits) > 0:
        
        rhythm = splits.pop(0)
        
        # If a rhythm is already 1 chunk
        if sum(rhythm) == 16:
            output.append(rhythm)
            
        # There is nothing to split here
        if len(rhythm) == 1:
            if output is not None:
                    output.append(rhythm)
            
        else:
            
            # Find 'middle' of the rhythm
            i = divide_rhythm(rhythm)
            
            # If it divides into nice chunks
            if sum(rhythm[:i]) % 16 == 0:
                splits.append(rhythm[:i])
                splits.append(rhythm[i:])
             
            # If it doesn't
            else:
                if output is not None:
                    output.append(rhythm)
            
    return output
    
    
    
""" COLLECTING MINOR PROGRESSIONS """

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
        



""" WRITE RESULTS TO FILE """

# Write rhythms to file
with open('Patterns/Melody/rhythms (extraction).txt', 'w') as file:
    
    for progression in rhythms_selection:
        
        # Join the elements of the progression list into a string and write it to the file
        file.write(' '.join(map(str, progression)) + '\n')  