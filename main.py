'''Main script to measure sound level.'''
import logging

from prometheus_client import start_http_server, Gauge

from sound import PeakTech8005

logger = logging.getLogger("my-logger")

SOUND_LEVEL = Gauge("sound_dba", "Sound in dB(A)")
MAC_PORT = '/dev/tty.usbserial-0001'
RASPBERRY_PORT = '/dev/ttyUSB0'


def measure_sound(db_level):
    '''Sets current sound level.'''
    SOUND_LEVEL.set(db_level)


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    # Start up the server to expose the metrics.
    start_http_server(8009)
    pt = PeakTech8005(serial_port=MAC_PORT)
    # Generate requests.
    while True:
        curr_db_level = pt.stream()
        if curr_db_level != PeakTech8005.DATA_ERROR:
            measure_sound(curr_db_level)
