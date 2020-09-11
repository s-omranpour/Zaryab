from pynput import keyboard
import pyo

class Synth:
    def __init__(self):
        self.server = pyo.Server().boot()
        self.harmonics = {}
        ##  Defines one octave
        self.notes = {
            'a':110.0,
            'a#':116.54,
            'b':123.47,
            'c':130.81,
            'c#':138.59,
            'd':146.83,
            'd#':155.56,
            'e':164.81,
            'f':174.61,
            'f#':185.00,
            'g': 196.00,
            'g#':207.65
        }

    def make_sine(self, freq):
        return pyo.SuperSaw(freq, detune=0.8)
    
    def press_key(self, key):
        try:
            char = key.char
            if char in self.notes and char not in self.harmonics:
                self.harmonics[char] = self.make_sine(self.notes[char]).out()
        except:
            pass
    
    def release_key(self, key):
        try:
            char = key.char
            if char in self.notes and char in self.harmonics:
                del self.harmonics[char]
        except:
            pass

    def run(self):
        self.server.start()
        with keyboard.Listener(on_press=self.press_key, on_release=self.release_key) as listener:
            listener.join()

synth = Synth()
synth.run()