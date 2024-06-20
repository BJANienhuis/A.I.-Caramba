# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 15:28:36 2024

@author: beaun
"""

import random
from Random_Configuration import set_seed
set_seed()

from Player import Player

import time
import mido

from Metrics import levenshtein_distance, pairwise_difference, rhythm_grid



# Delays the off-beats for a more swingy feeling
SWING = 0.2

# each drum kit piece with its according MIDI channel
mapping = {
    'kick':         4,
    'snare':        5,
    'closed hat':   6,  # 1 in cymbals
    'open hat':     7,  # 2 in cymbals
    'ride':         8,  # 3 in cymbals
    'crash':        9,  # 4 in cymbals
    'low tom':      10, # 1 in percussion
    'mid tom':      11, # 2 in percussion
    'high tom':     12, # 3 in percussion
    }



class Drum_Player(Player):
    
    """ VARIABLES """
    
    ID = "Drums"
    attention = ['Chords', 'Melody']
    
    libraries = {
        'kick':         "Patterns/Drums/kick.txt",          # Kick patterns with a kick on 1
        'kick (off)':   "Patterns/Drums/kick (off).txt",    # Kick patterns without a kick on 1
        'snare':        "Patterns/Drums/snare.txt",         # Snare patterns with a snare on 2
        'hats (8)':     "Patterns/Drums/hats (8).txt",      # Hat that repeats each 8th note
        'hats (4)':     "Patterns/Drums/hats (4).txt",      # Hat that repeats each quarter note
        'ride':         "Patterns/Drums/ride.txt",
        'toms':         "Patterns/Drums/toms.txt"}
    
    general_preference = (2, 2, 3)
    
    
    
    """
    Given a length (segments of 16 bars) and a BPM, improvise.
    At the end, send a final signal so that the other agents may terminate as well
    """
    def run(self):
        
        super().run()
        
        # Final sync to get the others out of the loop
        self.sync(1, 0)
            


    """ BASE FUNCTIONS """

    """
    Create a random kick pattern, with at least n, and no more than m kicks
    """
    def kick(self, n = 1, m = 10):
        
        # determines whether the second half starts with a kick or not
        library = random.choice(['kick', 'kick (off)'])
        
        # Initialise
        kick = list()
        
        # Find apropriate kick pattern
        while sum(kick) < n or sum(kick) > m:
            kick = random.choice(self.libraries.get('kick')) + random.choice(self.libraries.get(library))

        return kick
    
    
    
    """
    Create a random kick pattern, with at least n, and no more than m kicks
    """
    def snare(self, n = 1, m = 10):
        
        # Choose the snare library
        library = random.choice(['snare'])
        
        # Initialise
        snare = list()
        
        # Find apropriate kick pattern
        while sum(snare) < n or sum(snare) > m:
            snare = random.choice(self.libraries.get(library)) + random.choice(self.libraries.get(library))

        return snare
    
    
    
    """
    Pick a random cymbal pattern
    """
    def cymbals(self):
        
        # Choose the cymbal library
        library = random.choices(['hats (8)', 'hats (4)'], weights = [0.6, 0.4])[0]
        
        # Choose random cymbal pattern
        cymbals = random.choice(self.libraries.get(library))

        return cymbals

    
    
    """
    Generate a random sequence
    """
    def random_sequence(self):
        
        kick = self.kick()
        snare = self.snare()
        cymbals = self.cymbals()
        percussion = [0 for _ in range(16)]
        
        drums = (kick, snare, cymbals, percussion)
        
        return drums
            
    
    
    """ SCORES """
    
    """
    Calculate the levenshtein difference of 2 internal representations of sequences
    """
    def similarity(self, s1, s2):
        
        # Calculate continuity with own internal representation
        similarity = 0
        for p1, p2 in zip(s1, s2):
            similarity += levenshtein_distance(p1, p2)
            
        return similarity
    
    
    
    """
    Calculate the difference in each sequence's drum hits
    """
    def energy_consistency(self, s1, s2):
        e1 = sum([sum(kit_piece) for kit_piece in s1])
        e2 = sum([sum(kit_piece) for kit_piece in s2])
        return abs(e1 - e2)
    
    
    
    """
    Calculate the pairwise differences of rhythm with another instrument
    """
    def rhythm_overlap(self, output, sequence):
        
        # Get drum rhythm grid
        kick, snare, cymbals, percussion = sequence
        s1 = [1 if kick == 1 or snare == 1 else 0 for (kick, snare) in zip(kick, snare)]
        
        # Get the rhythm grid from the output
        rhythm = [rhythm for _, rhythm in output]
        s2 = rhythm_grid(rhythm)
        
        return pairwise_difference(s1, s2)
        
        
    
    
    
    """ SUPERCLASS FUNCTION IMPLEMENTATIONS """   
    
    """
    Calculate the score of a sequence given a memory chunk
    """
    def score(self, memory, sequence):
        
        # Calculate metrics
        similarity = self.similarity(memory.get(self.ID), sequence)         if self.reflection else 0
        energy = self.energy_consistency(memory.get(self.ID), sequence)     if self.reflection else 0
        chords_match = self.rhythm_overlap(memory.get("Chords"), sequence)  if self.cooperation else 0
        # melody_match = self.rhythm_overlap(memory.get("Melody"), sequence)  if self.cooperation else 0
            
        return similarity, energy, chords_match
    
    
    
    """
    Given a base pattern, select a random set of kit pieces and swap their pattern
    """
    def sequence_variation(self, sequence):
        
        # Unpack kit pieces
        kick, snare, cymbals, percussion = sequence
        kick_new, snare_new, cymbals_new, percussion_new = sequence
                
        # Choose which kit piece to vary
        variation = ['kick', 'snare', 'cymbals'] # Percussion
        kit_pieces = random.randint(0, len(sequence) - 1)
        random.shuffle(variation)
        variation = variation[:kit_pieces] 
        
        for kit_piece in variation:
            
            if kit_piece == 'kick':
                kick_new = self.kick()
            
            elif kit_piece == 'snare':
                snare_new = self.snare()
                
            elif kit_piece == 'cymbals':
                cymbals_new = self.cymbals()
                
            elif kit_piece == 'percussion':
                pass
                
        return kick_new, snare_new, cymbals_new, percussion_new
    
    
    
    """
    Generate a starting sequence
    """
    def start_sequence(self):
        
        kick = self.kick(3, 5)
        snare = self.snare(2, 3)
        cymbals = self.cymbals()
        percussion = [0 for _ in range(16)]
        
        drums = (kick, snare, cymbals, percussion)
        
        return drums

    
    
    """
    Choose a sequence for the base of a section
    """
    def base_sequence(self):
        
        # Set metric preferences & weights
        similarity =    5,  2
        energy =        1,  3
        chords_match =  3,  1
        # melody_match =  5,  1
        
        metrics = similarity, energy, chords_match
        
        # Determine importance of each type of sequence in the phrase
        current =   1
        base =  	0
        section =   0
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics)
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
    
    
    
    """
    Make a variation on a given base pattern
    """
    def minor_variation(self):
        
        # Set metric preferences & weights
        similarity =    2,  2
        energy =        1,  2
        chords_match =  3,  1
        # melody_match =  5,  1
        
        metrics = similarity, energy, chords_match
        
        # Determine importance of each type of sequence in the phrase
        current =   1
        base =  	2
        section =   0
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics)
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
    
    
    
    """
    Make a variation on a given base pattern
    """
    def major_variation(self):
        
        # Set metric preferences & weights
        similarity =    5,  2
        energy =        5,  2
        chords_match =  2,  1
        # melody_match =  4,  1
        
        metrics = similarity, energy, chords_match
        
        # Determine importance of each type of sequence in the phrase
        current =   1
        base =  	2
        section =   0
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics)
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
    
    
    
    """
    Apply variation on a whole section, only making minor changes,
    to keep things both fresh and familiar
    """
    def section_variation(self):
        
        # Set metric preferences & weights
        similarity =    1,  2
        energy =        1,  2
        chords_match =  2,  1
        # melody_match =  4,  1
        
        metrics = similarity, energy, chords_match
        
        # Determine importance of each type of sequence in the phrase
        current =   1
        base =  	2
        section =   3
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics)
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
        
        
        
    """
    Generates a pattern for the end of a phrase, moving it into the next
    """
    def phrase_end(self):
        
        # Set metric preferences & weights
        similarity =    5,  3
        energy =        5,  3
        chords_match =  2,  1
        # melody_match =  4,  1
        
        metrics = similarity, energy, chords_match
        
        # Determine importance of each type of sequence in the phrase
        current =   3
        base =  	1
        section =   2
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics)
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
    
    
    
    """
    Converts a pattern to it's equivalent MIDI information
    """
    def convert(self, sequence):
        
        MIDI = []
        
        # Zip all of the kit pieces in the sequence
        kick, snare, cymbals, percussion = sequence
        sequence = zip(kick, snare, cymbals, percussion)
        
        for (kick, snare, cymbals, percussion) in sequence:
            
            step = []
            
            # For each of the pieces, add it if it should be played
            if kick == 1:
                step.append('kick')
            if snare == 1:
                step.append('snare')
            if cymbals == 1:
                step.append('closed hat')
            elif cymbals == 2:
                step.append('open hat')
            elif cymbals == 3:
                step.append('ride')
            elif cymbals == 4:
                step.append('crash')
            if percussion == 1:
                step.append('low tom')
            elif percussion == 2:
                step.append('mid tom')
            elif percussion == 3:
                step.append('high tom')
            
            MIDI.append([step, 1])
        
        return MIDI
    
    
    
    """ OVERWRITTEN FUNCTIONS """
    
    """
    Activate a set of kit pieces through MIDI
    (Overwritten by the drummer)
    """
    def play(self, notes):    
        
        # Activate each kit piece seperately
        for piece in notes:
            
            # Get MIDI channel of kit piece
            channel = mapping.get(piece) - 1
            
            # Create and send MIDI message
            play = mido.Message('note_on', note = 60, velocity = 100, channel = channel)
            self.port.send(play)



    """
    Deactivate a set of notes through MIDI
    (Overwritten by the drummer)
    """
    def stop(self, notes):
        pass
    
    
    
    """
    Handle the timing condition
    """
    def sync(self, i: int, deliberation_time):
        
        # Calculate 16th note length based on BPM
        step = (60 / self.BPM) / 4
        
        # Add swing
        if i % 2 == 0:
            step -= SWING * step
        else:
            step += SWING * step
            
        time.sleep(step - deliberation_time)
        
        # Notify other threads to continue
        with self.timing:
            self.timing.notify_all()