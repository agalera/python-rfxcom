from unittest import TestCase

from rfxcom.protocol.temphumidity import TempHumidity

from rfxcom.exceptions import (InvalidPacketLength, UnknownPacketSubtype,
                               UnknownPacketType)


class TempHumidityTestCase(TestCase):

    def setUp(self):

        self.data = bytearray(b'\x0A\x52\x02\x11\x70\x02\x00\xA7'
                              b'\x2D\x00\x89')
        self.parser = TempHumidity()

    def test_parse_bytes(self):

        self.assertTrue(self.parser.validate_packet(self.data))
        self.assertTrue(self.parser.can_handle(self.data))
        result = self.parser.load(self.data)

        self.assertEquals(result, {
            'packet_length': 10,
            'packet_type': 82,
            'packet_type_name': 'Temperature and humidity sensors',
            'sequence_number': 17,
            'packet_subtype': 2,
            'packet_subtype_name': 'THGR810, THGN801, THGN800',
            'temperature': 16.7,
            'id': '0x7002',
            'channel': 2,
            'signal_level': 8,
            'humidity': 45,
            'humidity_status': 'Dry',
            'battery_level': 9
        })

        self.assertEquals(str(self.parser), "<TempHumidity ID:0x7002>")

    def test_parse_bytes2(self):

        self.data = bytearray(b'\x0A\x52\x02\x02\xAE\x01\x00\x63'
                              b'\x62\x03\x59')

        self.assertTrue(self.parser.validate_packet(self.data))
        self.assertTrue(self.parser.can_handle(self.data))
        result = self.parser.load(self.data)

        self.assertEquals(result, {
            'packet_length': 10,
            'packet_type': 82,
            'packet_type_name': 'Temperature and humidity sensors',
            'sequence_number': 2,
            'packet_subtype': 2,
            'packet_subtype_name': 'THGR810, THGN801, THGN800',
            'temperature': 9.9,
            'id': '0xAE01',
            'channel': 1,
            'signal_level': 5,
            'humidity': 98,
            'humidity_status': 'Wet',
            'battery_level': 9
        })

        self.assertEquals(str(self.parser), "<TempHumidity ID:0xAE01>")

    def test_parse_bytes_negative_temp(self):

        self.data = bytearray(b'\x0A\x52\x02\x11\x70\x02\x80\xA7'
                              b'\x2D\x00\x89')

        self.assertTrue(self.parser.validate_packet(self.data))
        self.assertTrue(self.parser.can_handle(self.data))
        result = self.parser.load(self.data)

        self.assertEquals(result['temperature'], -16.7)

    def test_validate_bytes_short(self):

        data = self.data[:1]

        with self.assertRaises(InvalidPacketLength):
            self.parser.validate_packet(data)

    def test_validate_unkown_packet_type(self):

        self.data[1] = 0xFF

        self.assertFalse(self.parser.can_handle(self.data))

        with self.assertRaises(UnknownPacketType):
            self.parser.validate_packet(self.data)

    def test_validate_unknown_sub_type(self):

        self.data[2] = 0xEE

        self.assertFalse(self.parser.can_handle(self.data))

        with self.assertRaises(UnknownPacketSubtype):
            self.parser.validate_packet(self.data)

    def test_log_name(self):

        self.assertEquals(self.parser.log.name, 'rfxcom.protocol.TempHumidity')
