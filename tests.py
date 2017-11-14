from functools import partial
import unittest
import djburger


class TestValidators(unittest.TestCase):

    def test_type_validator(self):
        # BASE
        with self.subTest(src_text='base pass'):
            v = djburger.v.TypeValidatorFactory(int)
            v = v(3)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.v.TypeValidatorFactory(int)
            v = v('3')
            self.assertFalse(v.is_valid())

        # BOOL
        with self.subTest(src_text='bool pass'):
            v = djburger.v.IsBoolValidator
            v = v(False)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='bool int not pass'):
            v = djburger.v.IsBoolValidator
            v = v(1)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='bool not pass'):
            v = djburger.v.IsBoolValidator
            v = v('1')
            self.assertFalse(v.is_valid())

        # INT
        with self.subTest(src_text='int pass'):
            v = djburger.v.IsIntValidator
            v = v(3)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='int bool not pass'):
            v = djburger.v.IsIntValidator
            v = v(True)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='int not pass'):
            v = djburger.v.IsIntValidator
            v = v('4')
            self.assertFalse(v.is_valid())

        # FLOAT
        with self.subTest(src_text='float pass'):
            v = djburger.v.IsFloatValidator
            v = v(3.2)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='float bool not pass'):
            v = djburger.v.IsFloatValidator
            v = v(True)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='float not pass'):
            v = djburger.v.IsFloatValidator
            v = v(4)
            self.assertFalse(v.is_valid())

        # STR
        with self.subTest(src_text='str pass'):
            v = djburger.v.IsStrValidator
            v = v('1')
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str empty pass'):
            v = djburger.v.IsStrValidator
            v = v('')
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str not pass'):
            v = djburger.v.IsStrValidator
            v = v(1)
            self.assertFalse(v.is_valid())

        # DICT
        with self.subTest(src_text='dict pass'):
            v = djburger.v.IsDictValidator
            v = v({1: 2})
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='dict empty pass'):
            v = djburger.v.IsDictValidator
            v = v({})
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='dict not pass'):
            v = djburger.v.IsDictValidator
            v = v([1, 2, 3])
            self.assertFalse(v.is_valid())

        # LIST
        with self.subTest(src_text='list pass'):
            v = djburger.v.IsListValidator
            v = v([1, 2])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list empty pass'):
            v = djburger.v.IsListValidator
            v = v([])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list tuple pass'):
            v = djburger.v.IsListValidator
            v = v((1, 2, 3))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list not pass'):
            v = djburger.v.IsListValidator
            v = v({})
            self.assertFalse(v.is_valid())

        # ITER
        with self.subTest(src_text='iter list pass'):
            v = djburger.v.IsListValidator
            v = v([1, 2])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter tuple pass'):
            v = djburger.v.IsListValidator
            v = v((1, 2))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter empty pass'):
            v = djburger.v.IsListValidator
            v = v([])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter str not pass'):
            v = djburger.v.IsListValidator
            v = v('123')
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='iter dict not pass'):
            v = djburger.v.IsListValidator
            v = v({1: 2, 3: 4})
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='iter not pass'):
            v = djburger.v.IsListValidator
            v = v(4)
            self.assertFalse(v.is_valid())

    def test_list_validator(self):
        with self.subTest(src_text='list int pass'):
            v = djburger.v.ListValidatorFactory(djburger.v.IsIntValidator)
            v = v([1, 2, 3])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list mixed not pass'):
            v = djburger.v.ListValidatorFactory(djburger.v.IsIntValidator)
            v = v([1, '2', 3])
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='list str pass'):
            v = djburger.v.ListValidatorFactory(djburger.v.IsStrValidator)
            v = v(['1', '2', '3'])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='tuple str pass'):
            v = djburger.v.ListValidatorFactory(djburger.v.IsStrValidator)
            v = v(('1', '2', '3'))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str not pass'):
            v = djburger.v.ListValidatorFactory(djburger.v.IsStrValidator)
            v = v('123')
            self.assertFalse(v.is_valid())

        with self.subTest(src_text='list list str pass'):
            v = djburger.v.ListValidatorFactory(
                djburger.v.ListValidatorFactory(
                    djburger.v.IsStrValidator
                )
            )
            v = v(data=[('1', '2'), ('3', '4', '5'), ('6', )])
            self.assertTrue(v.is_valid())

    def test_dict_mixed_validator(self):
        with self.subTest(src_text='dict int+str pass'):
            v = djburger.v.DictMixedValidatorFactory(validators={
                'ping': djburger.v.IsIntValidator,
                'pong': djburger.v.IsStrValidator,
            })
            v = v(data={
                'ping': 3,
                'pong': 'test',
            })
            self.assertTrue(v.is_valid())


if __name__ == '__main__':
    unittest.main()
