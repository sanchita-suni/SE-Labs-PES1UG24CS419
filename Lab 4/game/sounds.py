import array
import math
import random

import pygame

# All effects are synthesised at start-up from sine waves and filtered
# noise - no audio files and no extra libraries (only array, math, random).
#
#   whack      - wooden mallet "bonk": a low thump that drops in pitch, a
#                sharp crack of noise on impact, and a short 880 Hz bell
#                ding for the point.
#   miss       - the mallet swinging through air (a noise whoosh) and
#                landing on soft ground (a dull 180 Hz thud plus dirt).
#   pop        - a quiet rising "bloop" when a mole pops up.
#   round_over - descending arcade jingle 660 -> 520 -> 400 Hz, 0.15 s each.


def _osc(sr, seconds, freq, env, freq_end=None, harmonics=((1, 1.0),)):
    """Oscillator with an optional exponential pitch sweep and an
    amplitude envelope env(t, seconds) -> 0..1."""
    n = int(sr * seconds)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / sr
        f = freq if freq_end is None else freq * (freq_end / freq) ** (t / seconds)
        phase += 2 * math.pi * f / sr
        s = 0.0
        for mult, amp in harmonics:
            s += amp * math.sin(mult * phase)
        out.append(s * env(t, seconds))
    return out


def _noise(sr, seconds, env, rng, lowpass=1.0, highpass=0.0):
    """White noise through a one-pole low-pass (lower = darker) and an
    optional high-pass (higher = thinner), shaped by env(t, seconds)."""
    n = int(sr * seconds)
    out = []
    lp = 0.0
    slow = 0.0
    for i in range(n):
        t = i / sr
        lp += lowpass * (rng.uniform(-1.0, 1.0) - lp)
        slow += highpass * (lp - slow)
        out.append((lp - slow) * env(t, seconds))
    return out


def _mix(sr, *layers):
    """layers: (samples, start_seconds, gain). Returns their sum."""
    length = max(int(sr * start) + len(s) for s, start, _ in layers)
    out = [0.0] * length
    for samples, start, gain in layers:
        offset = int(sr * start)
        for i, v in enumerate(samples):
            out[offset + i] += v * gain
    return out


def _finish(sr, samples, peak, fade_out=0.015):
    """Normalise to `peak` (fraction of full scale), add a short fade-out
    so there is no click at the end, and convert to 16-bit integers."""
    loudest = max(abs(v) for v in samples) or 1.0
    scale = peak * 32767 / loudest
    fade = max(1, int(sr * fade_out))
    n = len(samples)
    result = []
    for i, v in enumerate(samples):
        remaining = n - i
        env = remaining / fade if remaining < fade else 1.0
        result.append(max(-32767, min(32767, int(v * scale * env))))
    return result


# Envelope shapes: env(t, seconds) -> 0..1
def _decay(tau):
    return lambda t, _s: math.exp(-t / tau)


def _attack_decay(attack, tau):
    return lambda t, _s: (t / attack) if t < attack else math.exp(-(t - attack) / tau)


def _swell(t, seconds):
    return math.sin(math.pi * t / seconds) ** 2


def build_effects(sr):
    """Return {name: list of int16 samples} for every effect."""
    rng = random.Random(7)   # fixed seed: the same sounds every run

    whack = _mix(
        sr,
        (_osc(sr, 0.16, 170, _decay(0.045), freq_end=55,
              harmonics=((1, 1.0), (2, 0.25))), 0.0, 1.0),        # thump
        (_noise(sr, 0.04, _decay(0.006), rng, lowpass=0.35), 0.0, 0.7),  # crack
        (_osc(sr, 0.22, 880, _decay(0.07),
              harmonics=((1, 1.0), (2, 0.35), (3, 0.1))), 0.012, 0.4),   # ding
    )

    miss = _mix(
        sr,
        (_noise(sr, 0.16, _swell, rng, lowpass=0.25, highpass=0.02), 0.0, 0.6),  # whoosh
        (_osc(sr, 0.12, 180, _decay(0.03), freq_end=110), 0.13, 0.8),           # thud
        (_noise(sr, 0.06, _decay(0.015), rng, lowpass=0.12), 0.13, 0.4),        # dirt
    )

    pop = _osc(sr, 0.07, 320, _swell, freq_end=900, harmonics=((1, 1.0), (2, 0.2)))

    jingle_layers = []
    for i, (freq, bend) in enumerate([(660, 660), (520, 520), (400, 370)]):
        note = _osc(sr, 0.15, freq, _attack_decay(0.005, 0.12), freq_end=bend,
                    harmonics=((1, 1.0), (2, 0.4), (3, 0.2)))
        jingle_layers.append((note, 0.15 * i, 1.0))
    round_over = _mix(sr, *jingle_layers)

    return {
        "whack": _finish(sr, whack, 0.75),
        "miss": _finish(sr, miss, 0.5),
        "pop": _finish(sr, pop, 0.15),
        "round_over": _finish(sr, round_over, 0.6),
    }


class Sounds:
    """Synthesised sound effects. Every method is a silent no-op if the
    mixer is unavailable, so the game runs normally without audio."""

    def __init__(self):
        self.enabled = False
        self.effects = {}
        self.pop_channel = None

        mixer_info = pygame.mixer.get_init()
        if not mixer_info:
            return
        sample_rate, _size, channels = mixer_info

        try:
            for name, samples in build_effects(sample_rate).items():
                if channels > 1:
                    # Mixer opened in stereo despite the request: duplicate samples.
                    samples = [s for s in samples for _ in range(channels)]
                self.effects[name] = pygame.mixer.Sound(buffer=array.array("h", samples))

            # Pops get one reserved channel, so a new pop cuts off the
            # previous one instead of piling up on busy (Hard) rounds.
            pygame.mixer.set_reserved(1)
            self.pop_channel = pygame.mixer.Channel(0)
            self.enabled = True
        except pygame.error:
            self.effects = {}

    def play(self, name):
        if not self.enabled or name not in self.effects:
            return
        if name == "pop":
            self.pop_channel.play(self.effects[name])
        else:
            self.effects[name].play()