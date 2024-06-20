# -*- coding: utf-8 -*-
"""
Created on Sun May  5 14:27:12 2024

@author: beaun
"""

""" IMPORTS """

import os
import mido



""" FUNCTIONS """

"""
Given a list of directories, collect all of the MIDI file paths
"""
def collect_paths(directories):
    
    files = []

    for directory in directories:
    
        # Iterate over all files in the directory
        for file in os.listdir(directory):
            
            # Construct full path MIDI file
            path = os.path.join(directory, file)
            
            files.append(path)
            
    return files



"""
Given a MIDI file path, turn it into a list of tuples ([a1, ..., an], l) where:
    [a1, ..., an] is a chord consisting the notes a1, ..., an
    l is the length of that chord in 16th notes
"""
def read_file(path):
    
    # Create MIDI object with mido
    MIDI = mido.MidiFile(path)
    
    # Get PPQ (number of ticks per quarter note)
    PPQ = MIDI.ticks_per_beat
    
    # Initialise variables
    to_16th = PPQ / 24
    playing = set()
    progression = list()
    
    for message in MIDI:
        
        # Chord end
        if message.time > 0:
            length = round(message.time * to_16th)
            chord = (playing.copy(), length)
            if length > 0:
                progression.append(chord)
        
        # Add note to 'currently playing'
        if message.type == 'note_on':
            note = message.note
            playing.add(note)
          
        # Remove note from 'currently playing'
        elif message.type == 'note_off':
            note = message.note
            if note in playing:
                playing.remove(note)
            
        # Calculate the 'conversion value'
        # (when multiplied with 'time', gives length in 16th notes)
        elif message.type == 'set_tempo':
            tempo = message.tempo
            to_16th = ((500000 / tempo) * PPQ) / 24
    
    return progression



"""
Removes any loops and returns the shortest non-looping segment
"""
def reduce(progression):
    
    # Calculate progressions total length
    length = len(progression)
    
    # Keep splitting the progression into equal parts
    while progression[:int(length/2)] == progression[int(length/2):length]:
        
        # cut length in half
        length = int(length/2)
        
    return progression[:length]