# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 15:45:39 2024

@author: beaun
"""

import threading

import mido
import time

from Scale import Scale

from Metrics import euclidian_distance

# Set phrase length
SECTIONS = 2



"""
TODO: add description
"""
class Player(threading.Thread):
    
    """ VARIABLES """
    
    ID: str
    attention: list
    libraries: dict
    
    # These variables are used to save and evaluate candidates
    candidates: dict
    general_preference: tuple
    
    # These variables are used to reconstruct and store the history of players
    long_memory: list
    short_memory: dict
    
    # These variables are used to control the amount of cooperation and self reflection
    reflection = True
    cooperation = False
    
    
    
    """ INITIALISATION """
    
    """
    Constructor
    """
    def __init__(self, root, mode, phrases, BPM, output, guides, port, channel):
        super().__init__()
        
        # Set initial variables
        self.scale = Scale(root, mode)
        self.phrases = phrases
        self.BPM = BPM
        self.output = output
        self.timing = guides[0]
        self.barrier = guides[1]
        self.lock = guides[2]
        self.port = port
        self.channel = channel - 1
        
        # Import pattern libraries
        self.import_libraries()
        
        # Initialise memories
        self.long_memory = list()
        self.reset_memory()
        
        # Calculate deliberation time based on BPM
        self.deliberation_time = ((60 / self.BPM) / 4) / 4
        
        # Initialise candidates list
        self.candidates = dict()
        
        
        
    """
    Import the patterns from the specified libraries.
    (Initially each library is mapped to a filepath)
    """
    def import_libraries(self):
        
        # Iterate the libraries
        for key in self.libraries.keys():
            
            # Read the file
            with open(self.libraries.get(key), 'r') as file:
                patterns = file.readlines()
            
            # Initialise list of progressions / rhythms
            library = list()
            
            # Iterate through each progression / rhythm
            for pattern in patterns:

                # Convert it to a list of integers
                pattern = pattern.strip().split()
                pattern = [int(char) for char in pattern]
                if len(pattern) > 0:
                    library.append(pattern)
            
            # Overwrite filepath with library
            self.libraries[key] = library
    
   
          
    """
    Return agent ID
    """
    def get_ID(self):
        return self.ID
        
        
        
    """ MAIN LOOP """
                
    """
    Given a number of phrases (segments of 16 bars) and a BPM, improvise
    """
    def run(self):
    
        # Play segments of 16 bars
        for phrase in range(self.phrases):
            
            # Create a base sequence for the phrase    
            if len(self.candidates.keys()) > 0:
                base = self.base_sequence()                
            else:
                base = self.start_sequence()
            
            # Calculate the sequence length
            sequence_length = sum([length for (_, length) in self.convert(base)])
            
            # Phrase length in 16th notes, (divided into 4 bar sections)
            length = SECTIONS * 64
            section = 0
            
            while length > 0:
                
                # count every 4 bar section
                if length % 64 == 0:
                    section += 1
                
                # Play base sequence at the start
                if length == SECTIONS * 64:
                    sequence = base
                
                # Vary for the rest of the section (of 4 bars)
                elif section == 1 and length % 64 == sequence_length:
                    sequence = self.major_variation()
                    
                # Vary for the rest of the section (of 4 bars)
                elif section == 1:
                    sequence = self.minor_variation()
                
                # Final sequence of the phrase
                elif length == sequence_length:
                    # TODO sequence = self.phrase_end()
                    sequence = self.section_variation()
                
                # Variate based on the previous section (of 4 bars)
                else:
                    sequence = self.section_variation()
                    
                # Reset candidate list
                self.candidates = {}    
                
                # Put sequence in short term memory
                self.short_memory[self.ID] = sequence
                    
                # Play the sequence
                self.play_sequence(sequence)
                
                # Subtract the sequences length
                length -= sequence_length
        
          
        
    """ PLAYING """            
                                
    """
    Takes a sequence, turns it to MIDI and plays it.
    It does so by counting in steps of 16th notes and starting / stopping chords accordingly.
    While doing this, it also writes its output to a common dictionary and reads the other outputs.
    """
    def play_sequence(self, sequence):
        
        # Convert sequence to MIDI information
        MIDI = self.convert(sequence)
        
        # Starting variables
        length = 0
        playing = False
        notes = None
        
        # Calculate length of MIDI sequence (in 16th notes)
        sequence_length = sum([length for (_, length) in MIDI])
        
        # Create iterator
        chord = iter(MIDI)
        
        # Sequence split into 16th notes
        for step in range(sequence_length):                
            
            # At the start, or if the chord / note is finished
            if length == 0:
                
                # Stop the chord / note (if playing)
                if playing:
                    self.stop(notes)
                    playing = False
                
                # Load the next chord / note
                notes, length = next(chord)
                
            # Consider candidates for the next sequence and return how long it took
            deliberation_time = self.deliberate(self.deliberation_time)
                
            # Either wait or signal depending on the player
            self.sync(step, deliberation_time)
                
            # To prevent it from repeating each 16th note
            if not playing:
                
                # Play the chord / note and update output
                playing = True
                self.play(notes)
                self.update(notes)
                
            else:
                
                self.sustain()
            
            # Read other agents' outputs
            self.listen()
            
            # Update to remaining length
            length -= 1
            
            # Write everything to memory after every bar
            if (step + 1) % 16 == 0:
                self.update_memory()

        self.stop(notes)
        
            
    
    """
    Activate a set of notes through MIDI
    (Overwritten by the drummer)
    """
    def play(self, notes):
        
        # If only 1 note is given (as an int)
        if type(notes) == int:
            notes = [notes]
        
        # Activate each note seperately
        for note in notes:
            
            # Create and send MIDI message
            play = mido.Message('note_on', note = note, velocity = 100, channel = self.channel)
            self.port.send(play)



    """
    Deactivate a set of notes through MIDI
    (Overwritten by the drummer)
    """
    def stop(self, notes):
        
        # If only 1 note is given (as an int)
        if type(notes) == int:
            notes = [notes]
        
        # Deactivate each note seperately
        for note in notes:
            
            # Send MIDI message
            stop = mido.Message('note_off', note = note, channel = self.channel)
            self.port.send(stop)
    
    
    
    """ NON VERBAL COMMUNICATION """
    
    """
    Update the agent's current output to the given input.
    Also sets the 'playing' variable to 1, indicating that a new chord / note is playing
    """
    def update(self, notes):
        
        # Make sure that only 1 thread writes at a time
        with self.lock:
            self.output[self.ID] = [notes, 1] 
            
            
            
    """
    Set the 'playing' variable to 0, indicating that the same chord / note is still playing
    """
    def sustain(self):
        
        # Make sure that only 1 thread writes at a time
        with self.lock:
            self.output[self.ID][1] = 0 
    
    
    
    """
    Reconstruct the playing pattern of other agents.
    A negative length annotates that a chord / note is still playing from last sequence. 
    """
    def listen(self):
        
        # Wait for others to finish writing
        self.barrier.wait()
        
        # Cycle the players attented to
        for ID in self.attention:
            
            # If a new chord / note is played
            if self.output[ID][1] == 1:
                self.short_memory[ID].append(self.output[ID].copy())
            
            # If the same chord is still playing
            else:
                
                # If the chord is sustained from the last sequence
                if len(self.short_memory[ID]) == 0:
                    self.short_memory[ID].append(self.output[ID].copy())
                    self.short_memory[ID][-1][1] = -1
                   
                # If the chord (started within the sequence) is sustained
                elif self.short_memory[ID][-1][1] > 0:
                    self.short_memory[ID][-1][1] += 1
                   
                # If the chord (started outside the sequence) is sustained
                else:
                    self.short_memory[ID][-1][1] -= 1
            
    
    
    """
    Handle the timing condition.
    (Overwritten by the drummer)
    (i is used for the drummer to add 'swing')
    """
    def sync(self, i: int, deliberation_time):
        
        # Wait for the drummer
        with self.timing:
            self.timing.wait()
                
    
    
    """ MEMORY MANAGEMENT """
    
    """
    Save everything to long memory and reset the short memory
    """
    def update_memory(self):
        
        # Save output reconstruction
        self.long_memory.append(self.short_memory)
        
        # Reset short memory
        self.reset_memory()
        
        
    
    """
    Create a clean short term memory dictionary,
    also discard unnecessary long term memory
    """
    def reset_memory(self):
        
        # Create an empty short memory
        empty = dict()
        for ID in self.attention + [self.ID]:
            empty[ID] = []            
        self.short_memory = empty
        
        # Wipe the last phrase when the first segment of a new phrase is saved
        if len(self.long_memory) > SECTIONS * 4:
            self.long_memory = self.long_memory[SECTIONS * 4:]
        
        
        
    """ SEQUENCE CONSIDERATION """     
    
    """
    Consider candidates for a specified amount of time,
    save the best candidates for later use.
    """
    def deliberate(self, deliberation_time):
        
        start = time.time()
        
        # Re-evaluate top sequence
        if len(self.candidates.keys()) > 0:
            self.update_scores(3)
        
        # Determine what sequence to base the variation on
        
        # 2nd sequence: Base it on the internal representation of the current sequence
        if len(self.long_memory) == 0 or len(self.long_memory) == SECTIONS * 4:
            sequence = self.short_memory.get(self.ID)
            
        # 3rd & 4th sequence: Base it on the first sequence of the phrase
        elif len(self.long_memory) in [1, 2]:
            sequence = self.long_memory[0].get(self.ID)
        
        # End of phrase sequence: base it on the accoriding sequence in the first section
        elif len(self.long_memory) == SECTIONS * 4 - 2:
            i = (len(self.long_memory) + 1) % 4
            sequence = self.long_memory[i].get(self.ID)
            # sequence = "end"
        
        # Starting sequence of next phrase: create a new starting sequence
        elif len(self.long_memory) == SECTIONS * 4 - 1:
            sequence = "start"
            
        # Sequences after the first section, base them on the according sequence in the first section
        else:
            i = (len(self.long_memory) + 1) % 4 
            sequence = self.long_memory[i].get(self.ID)
            
        current = time.time()
        
        # Keep creating and evaluating new patterns for a given amount of time
        while current - start < deliberation_time:
            
            if sequence == "start":
                variation = self.start_sequence()

            else:
                variation = self.sequence_variation(sequence)
            
            self.evaluate_sequence(variation)
            
            current = time.time()
        
        # Return how long it actually took
        return time.time() - start
    
    
    
    """
    TODO
    """
    def evaluate_sequence(self, sequence):
        
        # Score of the sequence against the current reconstruction
        current = self.score(self.short_memory, sequence)
        
        # Score of the sequence against the first sequence of the phrase
        base = tuple()
        if len(self.long_memory) in range(1, SECTIONS * 2 + 1):
            base = self.score(self.long_memory[0], sequence)
        
        # Score of the sequence against the matching sequence of the previous section
        section = tuple()
        if len(self.long_memory) in range(4, SECTIONS * 2 + 1):
            section = self.score(self.long_memory[-4], sequence)
            
        scores = current, base, section
        
        self.candidates[scores] = sequence
        
        
        
    """
    Evaluate a set of scores given a preference and weights.
    The scores are for each sequence it is matches against.
    the weights determines the importance of each sequence.
    """
    def evaluate_scores(self, scores, preferences):
        
        # The if statement is there for the cases where all of the tuples only contain 1 instance (and are therefore an int)
        metric_values, metric_weights, sequence_weights = zip(*preferences) if type(preferences[0]) == tuple else preferences
        
        total = 0
        for score, weight in zip(scores, sequence_weights):
            total += euclidian_distance(score, metric_values, metric_weights) * weight           
        return total
    
    
    
    """
    Evaluates only the first score (against current pattern) by matching it against a general preference
    """
    def evaluate_current(self, scores):
        score = scores[0] if type(scores[0]) == tuple else scores[0]
        return euclidian_distance(score, self.general_preference)
        
        
        
        
    """
    Given the candidates, a preference and a set of weights, find the best candidate 
    """
    def select_candidate(self, preferences):
        candidates = self.candidates.keys()
        best = min(candidates, key = lambda scores: self.evaluate_scores(scores, preferences))
        return self.candidates.get(best)
    
    
    
    """
    Re-evaluate the [number] most promising sequence (based on the current incomplete information)
    """
    def update_scores(self, number = 1):
        
        # Find the most promising sequence(s) (based on the incomplete short term memory)
        candidates = self.candidates.keys()
        selection = sorted(candidates, key = lambda scores: self.evaluate_current(scores))[:number]
        
        # Re-evaluate each of the best sequences
        for scores in selection:
            current, base, section = scores
            
            # Remove the key and sequence from the candidate list
            sequence = self.candidates.pop(scores)
            
            # Re-evaluate the scores with an updated short term memory
            current = self.score(self.short_memory, sequence)
            scores = current, base, section
            
            # Update the score
            self.candidates[scores] = sequence
        
        
    
    """ SUBCLASS SPECIFIC IMPLEMENTATIONS """
        
    """
    Calculate the score of a sequence given a memory chunk
    """
    def score(self, memory, sequence):
        pass
    
    
    
    """
    Generate a random variation given a sequence
    """
    def sequence_variation(self, sequence):
        pass 
    
    
    
    """
    Generate a base sequence
    """
    def start_sequence(self):
        pass
    
    
    
    """
    Generate a base sequence
    """
    def base_sequence(self):
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
    """
    def convert(self, sequence):
        pass