"""
Energy Usage Sensors
====================

"""

from rfxcom.protocol.base import BasePacketHandler
from rfxcom.protocol.rfxpacketutils import RfxPacketUtils


class Elec(BasePacketHandler):
    """The Elec protocol is a 17 byte packet used by energy sensors. The
    sensors transmit this packet periodically and the key data it provides is
    the current watt usage and total watt usage. It is used for example by the
    Owl energy monitors.

    ====    ====
    Byte    Meaning
    ====    ====
    0       Packet Length, 0x11 (excludes this byte)
    1       Packet Type, 0x5A
    2       Sub Type
    3       Sequence Number
    4       ID 1
    5       ID 2
    6       Count (?)
    7       Current Watts 1
    8       Current Watts 2
    9       Current Watts 3
    10      Current Watts 4
    11      Total Watts 1
    12      Total Watts 2
    13      Total Watts 3
    14      Total Watts 4
    15      Total Watts 5
    16      Total Watts 6
    17      RSSI and Battery Level
    ====    ====
    """
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.PACKET_TYPES = {
            0x5A: "Energy usage sensors"
        }
        self.PACKET_SUBTYPES = {
            0x01: "CM119/160",
            0x02: "CM180",
        }

    def _bytes_to_uint_32(self, bytes_):
        """Converts an array of 4 bytes to a 32bit integer.

        :param data: bytearray to be converted to a 32bit integer
        :type data: bytearray

        :return: the integer
        :rtype: int
        """
        return ((bytes_[0] * pow(2, 24)) +
                (bytes_[1] << 16) + (bytes_[2] << 8) + bytes_[3])

    def _bytes_to_uint_48(self, bytes_):
        """Converts an array of 6 bytes to a 48bit integer.

        :param data: bytearray to be converted to a 48bit integer
        :type data: bytearray

        :return: the integer
        :rtype: int
        """
        return ((bytes_[0] * pow(2, 40)) + (bytes_[1] * pow(2, 32)) +
                (bytes_[2] * pow(2, 24)) + (bytes_[3] << 16) +
                (bytes_[4] << 8) + bytes_[4])

    def parse(self, data):
        """Parse a 18 bytes packet in the Electricity format and return a
        dictionary containing the data extracted. An example of a return value
        would be:

        .. code-block:: python

            {
                'count': 3,
                'current_watts': 692,
                'id': "0x2EB2",
                'packet_length': 17,
                'packet_type': 90,
                'packet_type_name': 'Energy usage sensors',
                'sequence_number': 0,
                'packet_subtype': 1,
                'packet_subtype_name': "CM119/160",
                'total_watts': 920825.1947099693,
                'signal_level': 9,
                'battery_level': 6,
            }

        :param data: bytearray to be parsed
        :type data: bytearray

        :return: Data dictionary containing the parsed values
        :rtype: dict
        """

        self.validate_packet(data)

        TOTAL_DIVISOR = 223.666

        id_ = self.dump_hex(data[4:6])
        count = data[6]
        instant = data[7:11]
        total = data[11:16]

        current_watts = self._bytes_to_uint_32(instant)
        total_watts = self._bytes_to_uint_48(total) / TOTAL_DIVISOR

        sensor_specific = {
            'count': count,
            'current_watts': current_watts,
            'id': id_,
            'total_watts': total_watts
        }

        results = self.parse_header_part(data)
        results.update(RfxPacketUtils.parse_signal_and_battery(data[17]))
        results.update(sensor_specific)

        return results
