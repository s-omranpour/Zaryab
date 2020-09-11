from pynput import keyboard
from pyo import *

class Loop:
    def __init__(self, bpm=125):
        self.server = Server().boot()
        self.harmonics = {}
        self.key_mappings = {
            'a': self.make_kick,
            'b': self.make_bass,
            'c': self.make_closed_hihat,
            'd': self.make_chord1,
            'e': self.make_chord2,
            'f': self.make_bass2,
            'g': self.make_hihat,
            'h': self.make_Blit
        }
        
        self.bpm = bpm
        # Metronomes
        self.bar_met = Metro(bpm / 60.0).play()
        self.four_bar_met = Metro(bpm / 15).play()
        self.kick_met = Metro(bpm / 240.0).play()
        self.offbeat_met = Metro(bpm / 480.0).play()

        # Counters
        self.kick_counter = Counter(self.kick_met, min=0, max=4)
        self.offbeat_counter = Counter(self.offbeat_met, min=0, max=8)
        self.offbeat = Select(self.offbeat_counter % 2, 1)
        self.offbeat_2 = Select(self.offbeat_counter % 2, 1)

        # Timings
        beat_s = 60 / 125.0
        self.bar_s = beat_s * 4
        self.four_bar_s = self.bar_s * 4

    def make_kick(self):
        # Kick
        kick_env = CosTable([(0, 0), (10, 1), (1000, 0.5), (8191, 0)])
        kick_trigger = TrigEnv(self.kick_met, table=kick_env, dur=0.45, mul=0.5)
        return Sine(freq=61, mul=kick_trigger).mix(2).out()

    def make_hihat(self):
        # Open Hi-hat
        hat_env = LinTable([(0, 0), (100, 1), (800, 0.7), (8191, 0)])
        hat_trigger = TrigEnv(self.offbeat, hat_env, dur=0.2, mul=0.3)
        return (Noise(0.1).mix(2) * hat_trigger).out()

    def make_closed_hihat(self):
        # Closed Hi-hats
        hat_2_env = CosTable([(0, 0), (100, 1), (200, 0.1), (800, 0)])
        hat_2_pattern = Beat(time=self.bpm / 960.0, taps=16, w1=0, w2=40, w3=60).play()
        hat_2_trigger = TrigEnv(hat_2_pattern, hat_2_env)
        return (Noise(0.03).mix(2) * hat_2_trigger).out()

    def make_bass(self):
        # Bass
        bass_mid = TrigXnoiseMidi(self.offbeat_counter, dist=12, mrange=(38, 48))
        bass_hz = Snap(bass_mid, choice=[0, 2, 3], scale=1)
        bass_env = CosTable([(0, 0), (500, 1), (1000, 0.8), (8191, 0)])
        bass_trigger = TrigEnv(self.offbeat_2, bass_env, dur=0.4, mul=0.3)
        return SumOsc(
            freq=[bass_hz, bass_hz - 1],
            ratio=[0.2498, 0.2503],
            index=bass_trigger,
            mul=bass_trigger,
        ).out()
    
    def make_chord1(self):
        # Chord
        chord_count = Counter(self.kick_met, min=0, max=8)
        chord_start = Select(chord_count, 4)
        chord_trigger = NextTrig(self.bar_met, chord_start)
        chord_env = CosTable([(0, 0), (3000, 1), (4000, 0.5), (5500, 0.6), (8191, 0)])
        melody = [midiToHz(m) for m in [48, 50, 51.93, 53, 55.01, 57, 59, 60]]
        dur = RandDur(min=self.bpm / 240.0, max=self.bpm / 120.0)
        amp = TrigEnv(chord_trigger, table=chord_env, dur=dur, mul=0.5)
        saw = SuperSaw(freq=melody, detune=0.65, bal=0.7, mul=amp)
        filter = MoogLP(saw, freq=880, res=0.5)
        return Delay(filter, delay=[self.bpm / 240.0, self.bpm / 480.0], feedback=0.3, mul=0.5).out()

    def make_chord2(self):
        # Chord 2
        chord_env_2 = CosTable([(0, 0), (3000, 0.4), (5000, 1), (5500, 0.6), (8191, 0)])
        melody_2 = [midiToHz(m) / 2 for m in [48, 50, 51.93, 53, 55.01, 57, 59, 60]]
        dur_2 = RandDur(min=self.bpm / 180.0, max=self.bpm / 120.0)
        amp_2 = TrigEnv(self.four_bar_met, table=chord_env_2, dur=dur_2, mul=0.3)
        saw_2 = SuperSaw(freq=melody_2, detune=0.8, bal=0.7, mul=amp_2)
        filter_2 = MoogLP(saw_2, freq=770, res=0.8)
        delayed_2 = Delay(filter_2, delay=[self.bpm / 240.0, self.bpm / 480.0], feedback=0.3, mul=0.2)
        return Disto(delayed_2).out()

    def make_bass2(self):
        # Bass2
        t = CosTable([(0, 0), (100, 1), (500, 0.3), (8191, 0)])
        # melody_pattern = Beat(time=bpm/960.0, taps=16, w1=60, w2=10, w3=50, poly=1).play(delay=four_bar_s)
        melody_pattern = Beat(time=self.bpm / 960.0, taps=16, w1=60, w2=10, w3=50, poly=1).play(
            delay=7.68
        )
        trmid = TrigXnoiseMidi(melody_pattern, dist=12, mrange=(48, 60))
        trhz = Snap(trmid, choice=[0, 3], scale=1)
        tr2 = TrigEnv(
            melody_pattern, table=t, dur=melody_pattern["dur"], mul=melody_pattern["amp"]
        )
        f = FM(carrier=trhz, ratio=[0.2498, 0.2503], index=tr2, mul=tr2 * 0.3)
        return Disto(f, drive=0.85, mul=0.2).out()

    def make_Blit(self):
        # Blit
        blit_env = CosTable([(0, 0), (100, 1), (200, 0.1), (800, 0)])
        blit_pattern = Beat(time=bpm / 960.0, taps=16, w1=20, w2=20, w3=30).play(
            delay=2 * four_bar_s
        )
        blit_trigger = TrigEnv(blit_pattern, blit_env)
        lfo = Sine(freq=4, mul=0.02, add=1)
        lfo2 = Sine(freq=0.25, mul=10, add=30)
        return Blit(freq=[100, 99.7] * lfo, harms=lfo2, mul=0.2 * blit_trigger).out()
    
    def press_key(self, key):
        try:
            char = key.char
            if char in self.key_mappings:
                if char not in self.harmonics:
                    self.harmonics[char] = self.key_mappings[char]()
                else:
                    del self.harmonics[char]
            
        except:
            pass
    
    # def release_key(self, key):
    #     try:
    #         char = key.char
    #         if char in self.harmonics:
    #             del self.harmonics[char]
    #     except:
    #         pass

    def run(self):
        self.server.start()
        with keyboard.Listener(on_press=self.press_key) as listener:
            listener.join()

loop = Loop()
loop.run()