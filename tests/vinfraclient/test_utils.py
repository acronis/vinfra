from unittest import TestCase

from vinfraclient.utils import get_size_in_bytes


class TestGetSizeInBytes(TestCase):

    def test_positive(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.assertEqual(get_size_in_bytes("10"), 10)
        self.assertEqual(get_size_in_bytes("10KiB"), 10240)
        self.assertEqual(get_size_in_bytes("10MiB"), 10485760)
        self.assertEqual(get_size_in_bytes("10GiB"), 10737418240)
        self.assertEqual(get_size_in_bytes("10TiB"), 10995116277760)
        self.assertEqual(get_size_in_bytes("10PiB"), 11258999068426240)

        self.assertEqual(get_size_in_bytes("   10KiB"), 10240)
        self.assertEqual(get_size_in_bytes("    10KiB     "), 10240)
        self.assertEqual(get_size_in_bytes("10KiB    "), 10240)

    def test_negative(self, *args, **kwargs):  # pylint: disable=unused-argument
        with self.assertRaises(ValueError):
            get_size_in_bytes("")
        with self.assertRaises(ValueError):
            get_size_in_bytes("KiB")
        with self.assertRaises(ValueError):
            get_size_in_bytes("KiB10")
        with self.assertRaises(ValueError):
            get_size_in_bytes(10)
        with self.assertRaises(ValueError):
            get_size_in_bytes({"a": "b"})
        with self.assertRaises(ValueError):
            get_size_in_bytes("10KiBKiB")
        with self.assertRaises(ValueError):
            get_size_in_bytes("test")
        with self.assertRaises(ValueError):
            get_size_in_bytes("10 Kib")
        with self.assertRaises(ValueError):
            get_size_in_bytes("a   10K")
        with self.assertRaises(ValueError):
            get_size_in_bytes("10kib")
