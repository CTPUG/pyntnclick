# Generate 'perfect' sine wave sounds

# Design notes: produces ~= (use requested) s raw CDDA audio - 44100 Hz
#                           16 bit signed values
# Input is freq in Hz - 440 for A, etc. - must be an integer
# Output is written the file beep<freq>.pcm
# Convert to ogg with oggenc -r <file>

import sys
import math
import struct

CDDA_RATE = 44100
MAX = 105 * 256  # Max value for sine wave


def gen_sine(freq, secs):
    filename = 'beep%s.pcm' % freq
    # We need to generate freq cycles and sample that CDDA_RATE times
    samples_per_cycle = CDDA_RATE / freq
    data = []
    for x in range(samples_per_cycle):
        rad = float(x) / samples_per_cycle * 2 * math.pi
        y = MAX * math.sin(rad)
        data.append(struct.pack('<i', y))
    output = open(filename, 'w')
    for x in range(int(freq * secs)):
        output.write(''.join(data))
    output.close()


if __name__ == "__main__":
    freq = int(sys.argv[1])
    if len(sys.argv) > 2:
        secs = float(sys.argv[2])
    else:
        secs = 0.25
    gen_sine(freq, secs)
