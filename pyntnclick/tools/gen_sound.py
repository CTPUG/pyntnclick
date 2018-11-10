# Generate 'perfect' sine wave sounds

# Design notes: produces ~= (use requested) s raw CDDA audio - 44100 Hz
#                           16 bit signed values
# Input is freq in Hz - 440 for A, etc. - must be an integer
# Output is written the file beep<freq>.pcm
# Convert to ogg with oggenc -r <file>

from __future__ import print_function, division

import sys
import math
import struct

CDDA_RATE = 44100
MAX = 105 * 256  # Max value for sine wave


def gen_sine(freq, secs):
    filename = 'beep%s.pcm' % freq
    # We need to generate freq cycles and sample that CDDA_RATE times
    samples_per_cycle = CDDA_RATE // freq
    data = []
    for x in range(samples_per_cycle):
        rad = x / samples_per_cycle * 2 * math.pi
        y = MAX * math.sin(rad)
        data.append(struct.pack('<i', y))
    output = open(filename, 'w')
    for x in range(int(freq * secs)):
        output.write(''.join(data))
    output.close()
    return filename


def usage():
    print('Unexpected input')
    print('Usage: gen_sound.py <freq> [<length>]')
    print(' where <freq> is the frequency in Hz (integer)')
    print(' and [<length>] is the time is seconds (float)')


if __name__ == "__main__":
    try:
        freq = int(sys.argv[1])
    except Exception as exc:
        usage()
        print('Error was: %s' % exc)
        sys.exit(1)

    if len(sys.argv) > 2:
        try:
            secs = float(sys.argv[2])
        except Exception as exc:
            usage()
            print('Error was: %s' % exc)
            sys.exit(1)
    else:
        secs = 0.25
    output = gen_sine(freq, secs)
    print('Wrote sample to %s' % output)
