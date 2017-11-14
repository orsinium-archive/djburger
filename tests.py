import unittest
import djburger


class TestValidators(unittest.TestCase):

    def test_type_validator(self):
        with self.subTest(src_text='base pass'):
            v = djburger.v.TypeValidator
            v = v(3, int)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.v.TypeValidator
            v = v('4', int)
            self.assertFalse(v.is_valid())

        with self.subTest(src_text='int pass'):
            v = djburger.v.IsIntValidator
            v = v(3)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='int not pass'):
            v = djburger.v.IsIntValidator
            v = v('4')
            self.assertFalse(v.is_valid())


if __name__ == '__main__':
    unittest.main()
