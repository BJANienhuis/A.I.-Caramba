# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:17:41 2024

@author: beaun
"""

import random
from Random_Configuration import set_seed
set_seed()

from Player import Player

from Invertor import invert_progression
from Combiner import combine

from Variations import turn_around, relative_variation, relative_progression
from Variations import split_rhythm, join_rhythm, shift_rhythm

from Metrics import levenshtein_distance, pairwise_difference, rhythm_grid



class Chord_Player(Player):
    
    """ VARIABLES """
    
    ID = "Chords" 
    attention = ['Drums', 'Melody']
    bass_output = None
    
    libraries = {
        'progressions': "Patterns/Chords/progressions.txt",
        'rhythms':      "Patterns/Chords/rhythms (16).txt"
        }
    
    general_preference = (2, 2, 2, 2)
    
    
    
    """  VARIATIONS """
    
    """
    Takes a chord progression, and variates it with the following probabilities:
        (30%): relative variation (1 chord)
        (30%): relative progression
        (40%): turn-around progression
    """
    def progression_variation(self, progression):
        
        # Options & probabilities
        variations = [('relative variation',    0.4), 
                      ('relative progression',  0.4), 
                      ('turn_around',           0.2)]
        
        # Pick variation
        options, weights = zip(*variations)
        variation = random.choices(options, weights = weights)[0]
        
        # Relative  (1 chord)
        if variation == 'relative variation':
            return relative_variation(progression, self.scale, 1)
        
        # Relative progression
        elif variation == 'relative progression':
            return relative_progression(progression, self.scale)
        
        # Turnaround
        elif variation == 'turn_around':
            return turn_around(progression, self.scale)
        
        
        
    """
    Takes a chords rhythm, and variates it with the following probabilities:
        (40%): split rhythm
        (20%): join rhythm
        (40%): shift rhythm
    """
    def rhythm_variation(self, rhythm):
        
        # Options & probabilities
        variations = [('split rhythm',  0.4), 
                      ('join rhythm',   0.2),
                      ('shift rhythm',  0.4)]
        
        # Pick variation
        options, weights = zip(*variations)
        variation = random.choices(options, weights = weights)[0]
        
        # split a chord
        if variation == 'split rhythm':
            return split_rhythm(rhythm)
        
        # join 2 chords
        elif variation == 'join rhythm':
            return join_rhythm(rhythm)
        
        # shift 2 chords
        elif variation == 'shift rhythm':
            return shift_rhythm(rhythm)
        
    
    
    """
    Given a progression, find a matching rhythm (with as many or more chords)
    """
    def random_rhythm(self, sequence):
        
        # Unpack sequence
        progression, _ = sequence
            
        # Get a random rhythm that is bigger than the progression
        rhythm = random.choice(self.libraries.get('rhythms'))
        tries = 1
        while len(rhythm) < len(progression):
            rhythm = random.choice(self.libraries.get('rhythms'))
            tries += 1
            
            # If it takes too long, return the original
            if tries > 10:
                return sequence[1]
            
        return rhythm
    
    
    
    """
    Given a rhythm, find a matching progression (with as many or less chords)
    """
    def random_progression(self, sequence):
        
        # Unpack sequence
        _, rhythm = sequence
            
        # Get a random rhythm that is bigger than the progression
        progression = random.choice(self.libraries.get('progressions'))
        tries = 1
        while len(progression) > len(rhythm):
            rhythm = random.choice(self.libraries.get('progressions'))
            tries += 1
            
            # If it takes too long, return the original
            if tries > 10:
                return sequence[0]
            
        return progression
    
    
    
    """
    Generate a random sequence
    """
    def random_sequence(self):
        
        # Get a random rhythm & progression
        progression = random.choice(self.libraries.get('progressions'))
        rhythm = random.choice(self.libraries.get('rhythms'))
        
        # Assure the rhythm sequence contains more chords than the progression
        # If it takes more than 5 tries, get another rhythm
        tries = 1
        while len(progression) > len(rhythm):
            tries += 1
            progression = random.choice(self.libraries.get('progressions'))
            if tries > 5:
                rhythm = random.choice(self.libraries.get('rhythms'))
                tries = 1
        
        return progression, rhythm
    
    
    
    """ SCORES """
    
    """
    Calculate the levenshtein difference of a sequence in respect to the agent itself
    """
    def continuity(self, memory, sequence):
        p1, r1 = memory.get(self.ID)
        p2, r2 = sequence
        continuity = levenshtein_distance(rhythm_grid(r1), rhythm_grid(r2)) + levenshtein_distance(p1, p2)
        return continuity
    
    
    
    """
    Calculate the difference in each sequence's amount of chords and chord changes
    """
    def energy_consistency(self, s1, s2):
        p1, r1 = s1
        p2, r2 = s2
        e1 = len(p1) + len(r1)
        e2 = len(p2) + len(r2)
        return abs(e1 - e2)
    
    
    
    """
    Calculate the pairwise differences of rhythm with another instrument (grid)
    """
    def rhythm_overlap(self, output_grid, sequence):
        _, rhythm = sequence
        rhythm_overlap = pairwise_difference(output_grid, rhythm_grid(rhythm))
        return rhythm_overlap
        
        
        
    """ SUPERCLASS FUNCTION IMPLEMENTATIONS """   
    
    """
    Calculate the score of a sequence given a memory chunk
    """
    def score(self, memory, sequence):

        drum_grid = [1 if 'kick' in step or 'snare' in step else 0 for step, _ in memory.get('Drums')]
        melody_grid = rhythm_grid([length for _, length in memory.get('Melody')])

        # Calculate metrics
        continuity = self.continuity(memory, sequence)                  if self.reflection else 0
        energy = self.energy_consistency(memory.get(self.ID), sequence) if self.reflection else 0
        drum_match = self.rhythm_overlap(drum_grid, sequence)           if self.cooperation else 0
        melody_match = self.rhythm_overlap(melody_grid, sequence)       if self.cooperation else 0
        
        return continuity, energy, drum_match, melody_match
    
    
    
    """
    Generate a random variation given a sequence
    """
    def sequence_variation(self, sequence):
        
        progression, rhythm = sequence
        
        # Options & probabilities
        variations = [('rhythm',                0.1), 
                      ('progression',           0.2),
                      ('both',                  0.15),
                      ('random (progression)',  0.1),
                      ('random (rhythm)',       0.2),
                      ('random (both)',         0.1),
                      ('none',                  0.05)]
        
        # Pick one
        options, weights = zip(*variations)
        variation = random.choices(options, weights = weights)[0]
        
        if variation == 'rhythm':
            return progression, self.rhythm_variation(rhythm)
        
        elif variation == 'progression':
            return self.progression_variation(progression), rhythm
        
        elif variation == 'both':
            return self.progression_variation(progression), self.rhythm_variation(rhythm)
        
        elif variation == 'random (progression)':
            return self.random_progression(sequence), rhythm
        
        elif variation == 'random (rhythm)':
            return progression, self.random_rhythm(sequence)
        
        elif variation == 'random (both)':
            return self.random_sequence()
        
        elif variation == 'none':
            return sequence
    
    
    
    """
    Generate a base sequence with a progression that contains at least 3 chords
    """
    def start_sequence(self):
        
        # Get a random rhythm & progression
        progression = random.choice(self.libraries.get('progressions'))
        rhythm = random.choice(self.libraries.get('rhythms'))
        
        # Assure the rhythm sequence contains more chords than the progression
        # If it takes more than 5 tries, get another rhythm
        tries = 1
        while len(progression) > len(rhythm) or len(progression) < 3:
            tries += 1
            progression = random.choice(self.libraries.get('progressions'))
            if tries > 5:
                rhythm = random.choice(self.libraries.get('rhythms'))
                tries = 1
        
        return progression, rhythm
    
    
    
    """
    Generate a base sequence
    """
    def base_sequence(self):
        
        # Set metric preferences & weights
        continuity =    5,  2
        energy =        1,  3
        drum_match =    3,  1
        melody_match =  3,  1
        
        metrics = continuity, energy, drum_match, melody_match
        
        # Determine importance of each type of sequence in the phrase
        current =   1
        base =  	0
        section =   0
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics) if type(metrics[0]) == tuple else metrics
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
    
    
    
    """
    Make a variation on a given base pattern
    """
    def minor_variation(self):
        
        # Set metric preferences & weights
        continuity =    2,  2
        energy =        2,  1
        drum_match =    3,  3
        melody_match =  3,  1
        
        metrics = continuity, energy, drum_match, melody_match
        
        # Determine importance of each type of sequence in the phrase
        current =   1
        base =  	2
        section =   0
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics) if type(metrics[0]) == tuple else metrics
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
    
    
    
    """
    Make a variation on a given base pattern
    """
    def major_variation(self):
        
        # Set metric preferences & weights
        continuity =    5,  2
        energy =        5,  3
        drum_match =    3,  1
        melody_match =  3,  1
        
        metrics = continuity, energy, drum_match, melody_match
        
        # Determine importance of each type of sequence in the phrase
        current =   1
        base =  	2
        section =   0
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics) if type(metrics[0]) == tuple else metrics
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
    
    
    
    """
    Apply variation on a whole section, only making minor changes,
    to keep things both fresh and familiar
    """
    def section_variation(self):
        
        # Set metric preferences & weights
        continuity =    2,  3
        energy =        1,  1
        drum_match =    3,  2
        melody_match =  3,  1
        
        metrics = continuity, energy, drum_match, melody_match
        
        # Determine importance of each type of sequence in the phrase
        current =   1
        base =  	2
        section =   3
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics) if type(metrics[0]) == tuple else metrics
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
        
        
        
    """
    Generates a pattern for the end of a phrase, moving it into the next
    """
    def phrase_end(self):
        
        # Set metric preferences & weights
        continuity =    5,  2
        energy =        5,  3
        drum_match =    3,  1
        melody_match =  3,  1
        
        metrics = continuity, energy, drum_match, melody_match
        
        # Determine importance of each type of sequence in the phrase
        current =   3
        base =  	1
        section =   2
        
        sequence_weights = current, base, section
        
        # Summarise everything in 1 variable
        metric_preferences, metric_weights = zip(*metrics) if type(metrics[0]) == tuple else metrics
        preferences = metric_preferences, metric_weights, sequence_weights
        
        return super().select_candidate(preferences)
    
    
    
    """
    Converts a pattern to it's equivalent MIDI information
    """
    def convert(self, sequence):
        
        # Split progression and rhythm
        progression, rhythm = sequence
        
        # Fill the rhythm with the progression
        progression = combine(progression, rhythm)
        
        # Send bass notes to bass player
        self.send_bass(progression, rhythm)
        
        # Turn progression into notes
        chords = [self.scale.triad(chord, - 1) for chord in progression]
        
        # Invert chords to be closer together
        chords = invert_progression(chords)
        
        # Zip contents
        MIDI = list(zip(chords, rhythm))
        
        return MIDI



    """ BASS """ 
  
    """
    Given a progression and rhythm, write the bassline and send it to the output
    """
    def send_bass(self, progression: list, rhythm: list):
        
        # Create bass notes
        notes = [self.scale.note(note, -3) for note in progression]
        
        # Create bassline
        bassline = list(zip(notes, rhythm))
        
        # Write bassline to dictionary
        with self.lock:
            self.output['Bass'] = bassline
            
        # Notify bass player
        self.bass_output.wait()