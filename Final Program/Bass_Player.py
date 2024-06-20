# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 12:24:11 2024

@author: beaun
"""

from Player import Player



"""
Mock class. This class recieves MIDI information from the chord player.
"""
class Bass_Player(Player):
    
    """ VARIABLES """
    
    ID = "Bass" 
    attention = []
    bass_output = None
    
    libraries = {
        }    
    
    general_preference = 0
    
    
    
    """ SUPERCLASS FUNCTION IMPLEMENTATIONS """ 
    
    """
    Calculate the score of a sequence given a memory chunk
    """
    def score(self, memory, sequence):
        pass
    
    
    
    """
    Generate a random sequence
    """
    def random_sequence(self):
        pass
    
    
    
    """
    Generate a base sequence
    """
    def base_sequence(self):
        pass
    
    
    
    """
    Generate a random variation given a sequence
    """
    def sequence_variation(self, sequence):
        pass
    
    
    
    """
    Make a variation on a given base pattern
    """
    def minor_variation(self):
        pass
    
    
    
    """
    Make a variation on a given base pattern
    """
    def major_variation(self):
        pass
    
    
    
    """
    Find the according sequence in the memory (based on the length and sequence length),
    pass it to the subclass implementation to process further.
    """
    def section_variation(self):
        pass
        
        
        
    """
    Generates a pattern for the end of a phrase, moving it into the next
    """
    def phrase_end(self):
        pass
    
    
    
    """
    Converts a pattern to it's equivalent MIDI information
    (Wait for the chord player to send a melody and import it)
    """
    def convert(self, sequence):
        
        # Wait for chord player input
        self.bass_output.wait()
            
        bassline = self.output.get(self.ID)
        
        return bassline