# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 18:42:59 2024

@author: beaun
"""

from Chord_Player import Chord_Player
from Melody_Player import Melody_Player
from Drum_Player import Drum_Player
from Bass_Player import Bass_Player
import time
import threading
import mido

# random.seed(42)

# To quickly turn on / off playing during testing
play = True

# Set scale, BPM and nr of phrases played
root = 'A'
mode = 'Minor'
BPM = 100
phrases = 1
print("\nScale:\t\t{:s} {:s}".format(root, mode))
print("BPM:\t\t{:d}".format(BPM))
print("Phrases:\t{:d}".format(phrases))

# Create thread guides
timing = threading.Condition()
barrier = threading.Barrier(4)
lock = threading.Lock()
guides = (timing, barrier, lock)

# Create output log
output = dict()

# The try statement is here so that the the MIDI port is always closed once it's created
try:
    
    # Create midi port
    available = mido.get_output_names()
    print("\nAvailable MIDI ports:", available)
    port = mido.open_output(available[-1])
    
    # Create player threads
    print("\nCreating players")
    bass = Bass_Player(root, mode, phrases, BPM, output, guides, port, channel = 1)
    chords = Chord_Player(root, mode, phrases, BPM, output, guides, port, channel = 2)
    melody = Melody_Player(root, mode, phrases, BPM, output, guides, port, channel = 3)
    drums = Drum_Player(root, mode, phrases, BPM, output, guides, port, channel = 4)
    players = [bass, chords, melody, drums]
    
    # This allows for a (temporary) communication channel between the bass & chord player
    bass_output = threading.Barrier(2)
    chords.bass_output = bass_output
    bass.bass_output = bass_output
    
    # Add players to output
    for player in players:
        output[player.get_ID()] = None
     
    if play:

        # Allows me to switch to FL studio
        time.sleep(3)
        
        # Start the players
        print("\nStarting players")
        for player in players:
            player.start()
        
        # Wait for the players to finish
        print("\nWaiting for players to finish")
        for player in players:
            player.join()

# Print error
except Exception as e:
    print("An error occurred:", e)

# Close the port
finally:
    print("\nClosing port")
    port.close()