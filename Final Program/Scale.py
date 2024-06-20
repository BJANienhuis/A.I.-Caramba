# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 14:05:12 2024

@author: beaun
"""

import numpy as np



MODES = {
    'Major':            [0, 2, 4, 5, 7, 9, 11],
    'Major Pentatonic': [0, 2, 4,    7, 9    ],
    'Minor':            [0, 2, 3, 5, 7, 8, 10],
    'Minor Pentatonic': [0,    3, 5, 7,    10],
    'Harmonic Minor':   [0, 2, 3, 5, 7, 8, 11],
    'Melodic Minor':    [0, 2, 3, 5, 7, 9, 11],
    'Dorian':           [0, 2, 3, 5, 7, 9, 10],
    'Phrygian':         [0, 1, 3, 5, 7, 8, 10],
    'Lydian':           [0, 2, 4, 6, 7, 9, 11],
    'Mixolydian':       [0, 2, 4, 5, 7, 9, 10],
    'Locrian':          [0, 1, 3, 5, 6, 8, 10],
    }



NOTES = {
    'C':    60,
    'C#':   61,
    'Db':   61,
    'D':    62,
    'D#':   63,
    'Eb':   63,
    'E':    64,
    'F':    65,
    'F#':   66,
    'Gb':   66,
    'G':    67,
    'G#':   68,
    'Ab':   68,
    'A':    69,
    'A#':   71,
    'Bb':   71,
    'B':    72,
    }



class Scale:
    
    root: int
    mode: str
    interval: list
    
    
    
    """
    Constructor
    """
    def __init__(self, root: str, mode: str):
        
        # Verify root note and mode
        assert root in NOTES, "{:s} is not a valid note!".format(root)
        assert mode in MODES, "{:s} {:s} is not a valid mode or hasn't been implemented!".format(root, mode)
       
        # Set variables
        self.root = NOTES.get(root)
        self.mode = mode
        self.interval = MODES.get(mode)
        
        
    
    """ MELODIC TOOLS """
    
    """
    Returns the nth note of the scale and modulates it up or down some octaves
    """
    def note(self, nr: int, octave = 0):
        
        # Verify that note is in scale
        assert nr <= self.size(), "There are only {:d} notes in this scale!".format(self.size())
        assert octave >= -5 and octave <= 10, "The note can not be modulated {:d} octaves!".format(octave)
        
        return self.root + self.interval[nr - 1] + octave * 12
    
    
    
    """
    Creates the nth 3 note chord of a scale and modulates it up or down some octaves
    """
    def triad(self, nr: int, octave = 0):
        
        # Verify if chord exists within scale
        assert nr <= self.size(), "There are only {:d} triads in this scale!".format(self.size())
        
        # Get chord notes
        nr -= 1
        root = self.root + self.interval[nr] + octave * 12
        second = self.root + self.interval[(nr + 2) % self.size()] + octave * 12
        third = self.root + self.interval[(nr + 4) % self.size()] + octave * 12
        
        # Check if notes cross the octave
        if nr + 2 >= self.size():
            second += 12
        if nr + 4 >= self.size():
            third += 12
            
        # Return chord
        return [root, second, third]
    
    
    
    """
    Creates the nth 4 note chord of a scale and modulates it up or down some octaves
    """
    def seventh(self, nr: int, octave = 0):
        
        # Verify if chord exists within scale
        assert nr <= self.size(), "There are only {:d} seventh chords in this scale!".format(self.size())
        
        # Get chord notes
        nr -= 1
        root = self.root + self.interval[nr] + octave * 12
        second = self.root + self.interval[(nr + 2) % self.size()] + octave * 12
        third = self.root + self.interval[(nr + 4) % self.size()] + octave * 12
        fourth = self.root + self.interval[(nr + 6) % self.size()] + octave * 12
        
        # Check if notes cross the octave
        if nr + 2 >= self.size():
            second += 12
        if nr + 4 >= self.size():
            third += 12
        if nr + 6 >= self.size():
            fourth += 12
            
        # Return chord
        return [root, second, third, fourth]
    
    
    
    """ SCALE SPECIFIC INFORMATION """
             
    """
    Returns the number of notes that are in the scale
    """
    def size(self):
        return len(self.interval)
    
    
    
    """
    Given a chord, find the corresponding relative chord in the scale.
    This relative chord should share 2 notes and therefore sound similar, but different.
    """
    def relative(self, nr: int):
        
        # Verify if chord exists within scale
        assert nr <= self.size(), "There are only {:d} root notes in this scale!".format(self.size())
        assert self.mode in ['Major', 'Minor', 'Harmonic Minor'], "Relative chords have only been implemented for major and minor scales."
        
        # relative chords are obtained by moving up 5 (from major to minor)
        if self.mode == 'Major':
            
            # major chords
            if nr in [1, 4, 5]:
                return (nr + 5) % 7
            
            # minor chords
            elif nr in [6, 2, 3]:
                return (7 + nr - 5) % 7
            
            # diminished chord
            else:
                return nr
        
        # relative chords are obtained by moving up 2 (from minor to major)
        elif self.mode in ['Minor', 'Harmonic Minor']:
            
            # minor chords
            if nr in [1, 4, 5]:
                return nr + 2
            
            # major chords
            if nr in [3, 6, 7]:
                return nr - 2
            
            # diminished chord
            else:
                return nr
            
            
    
    """
    Given a progression, try abstracting it to the chord positions on the scale.
    """
    def abstract_progression(self, progression):
        
        # List of all chords, modulo 12 for each note
        triads = [None]
        sevenths = [None]
        
        for nr in range(1, self.size() + 1):
            
            # Create fingerprint (each note modulo 12)
            chord = self.triad(nr)
            fingerprint = set([note % 12 for note in chord])
            triads.append(fingerprint)
            
            # Create fingerprint (each note modulo 12)
            chord = self.seventh(nr)
            fingerprint = set([note % 12 for note in chord])
            sevenths.append(fingerprint)
        
        # List of the progression's chords reduced to their position in the scale
        abstraction = []
        
        for chord in progression:
            
            fingerprint = set([note % 12 for note in chord])
            found = False
            
            # Try to match the fingerprint with a chord in the scale
            for nr in range(1, self.size() + 1):
                
                # The chord matches the fingerprint
                if triads[nr] == fingerprint or sevenths[nr] == fingerprint:
                    
                    abstraction.append(nr)
                    found = True
            
            # None of the chords match the fingerprint
            if not found:
                return None
            
        return abstraction
    
    
    
    """ OTHER TOOLS """
            
    """
    Modulate the root note up or down
    """
    def modulate(self, mod):
        self.root = (self.root + mod) % 12 + 60
        
        
        
    """
    Flip major to minor and vice versa
    """
    def flip_mode(self):
        
        # switch to minor
        if self.mode == 'Major':
            self.mode = 'Minor'
            self.interval = MODES.get('Minor') 
            
        # switch to major
        elif self.mode == 'Minor':
            self.mode = 'Major'
            self.interval = MODES.get('Major') 