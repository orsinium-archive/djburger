from __main__ import unittest, djburger


class MainValidatorsTest(unittest.TestCase):

    def test_type_validator(self):
        # BASE
        with self.subTest(src_text='base pass'):
            v = djburger.validators.constructors.Type(int)
            v = v(3)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.validators.constructors.Type(int)
            v = v('3')
            self.assertFalse(v.is_valid())

        # BOOL
        with self.subTest(src_text='bool pass'):
            v = djburger.validators.constructors.IsBool
            v = v(False)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='bool int not pass'):
            v = djburger.validators.constructors.IsBool
            v = v(1)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='bool not pass'):
            v = djburger.validators.constructors.IsBool
            v = v('1')
            self.assertFalse(v.is_valid())

        # INT
        with self.subTest(src_text='int pass'):
            v = djburger.validators.constructors.IsInt
            v = v(3)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='int bool not pass'):
            v = djburger.validators.constructors.IsInt
            v = v(True)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='int not pass'):
            v = djburger.validators.constructors.IsInt
            v = v('4')
            self.assertFalse(v.is_valid())

        # FLOAT
        with self.subTest(src_text='float pass'):
            v = djburger.validators.constructors.IsFloat
            v = v(3.2)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='float bool not pass'):
            v = djburger.validators.constructors.IsFloat
            v = v(True)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='float not pass'):
            v = djburger.validators.constructors.IsFloat
            v = v(4)
            self.assertFalse(v.is_valid())

        # STR
        with self.subTest(src_text='str pass'):
            v = djburger.validators.constructors.IsStr
            v = v('1')
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str empty pass'):
            v = djburger.validators.constructors.IsStr
            v = v('')
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str not pass'):
            v = djburger.validators.constructors.IsStr
            v = v(1)
            self.assertFalse(v.is_valid())

        # DICT
        with self.subTest(src_text='dict pass'):
            v = djburger.validators.constructors.IsDict
            v = v({1: 2})
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='dict empty pass'):
            v = djburger.validators.constructors.IsDict
            v = v({})
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='dict not pass'):
            v = djburger.validators.constructors.IsDict
            v = v([1, 2, 3])
            self.assertFalse(v.is_valid())

        # LIST
        with self.subTest(src_text='list pass'):
            v = djburger.validators.constructors.IsList
            v = v([1, 2])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list empty pass'):
            v = djburger.validators.constructors.IsList
            v = v([])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list tuple pass'):
            v = djburger.validators.constructors.IsList
            v = v((1, 2, 3))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list not pass'):
            v = djburger.validators.constructors.IsList
            v = v({})
            self.assertFalse(v.is_valid())

        # ITER
        with self.subTest(src_text='iter list pass'):
            v = djburger.validators.constructors.IsList
            v = v([1, 2])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter tuple pass'):
            v = djburger.validators.constructors.IsList
            v = v((1, 2))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter empty pass'):
            v = djburger.validators.constructors.IsList
            v = v([])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter str not pass'):
            v = djburger.validators.constructors.IsList
            v = v('123')
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='iter dict not pass'):
            v = djburger.validators.constructors.IsList
            v = v({1: 2, 3: 4})
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='iter not pass'):
            v = djburger.validators.constructors.IsList
            v = v(4)
            self.assertFalse(v.is_valid())

    def test_list_validator(self):
        with self.subTest(src_text='list int pass'):
            v = djburger.validators.constructors.List(djburger.validators.constructors.IsInt)
            v = v([1, 2, 3])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list mixed not pass'):
            v = djburger.validators.constructors.List(djburger.validators.constructors.IsInt)
            v = v([1, '2', 3])
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='list str pass'):
            v = djburger.validators.constructors.List(djburger.validators.constructors.IsStr)
            v = v(['1', '2', '3'])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='tuple str pass'):
            v = djburger.validators.constructors.List(djburger.validators.constructors.IsStr)
            v = v(('1', '2', '3'))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str not pass'):
            v = djburger.validators.constructors.List(djburger.validators.constructors.IsStr)
            v = v('123')
            self.assertFalse(v.is_valid())

        with self.subTest(src_text='list list str pass'):
            v = djburger.validators.constructors.List(
                djburger.validators.constructors.List(
                    djburger.validators.constructors.IsStr
                )
            )
            v = v(data=[('1', '2'), ('3', '4', '5'), ('6', )])
            self.assertTrue(v.is_valid())

    def test_dict_mixed_validator(self):
        with self.subTest(src_text='dict int+str pass'):
            v = djburger.validators.constructors.DictMixed(validators={
                'ping': djburger.validators.constructors.IsInt,
                'pong': djburger.validators.constructors.IsStr,
            })
            v = v(data={
                'ping': 3,
                'pong': 'test',
            })
            self.assertTrue(v.is_valid())

    def test_lambda_validator(self):
        with self.subTest(src_text='lambda int pass'):
            v = djburger.validators.constructors.Lambda(key=lambda data: data > 0)
            v = v(4)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='lambda int not pass'):
            v = djburger.validators.constructors.Lambda(key=lambda data: data > 0)
            v = v(-4)
            self.assertFalse(v.is_valid())

    def test_clean_validator(self):
        with self.subTest(src_text='lambda int pass'):
            v = djburger.validators.constructors.Clean(key=lambda data: int(data))
            v = v('4')
            v.is_valid()
            self.assertEqual(v.cleaned_data, 4)

    def test_chain_validator(self):
        with self.subTest(src_text='chain int pass'):
            v = djburger.validators.constructors.Chain([
                djburger.validators.constructors.IsInt,
                djburger.validators.constructors.Lambda(key=lambda data: data > 0),
            ])
            v = v(4)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='lambda int not pass'):
            v = djburger.validators.constructors.Chain([
                djburger.validators.constructors.IsInt,
                djburger.validators.constructors.Lambda(key=lambda data: data > 0),
            ])
            v = v(-4)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='lambda str not pass'):
            v = djburger.validators.constructors.Chain([
                djburger.validators.constructors.IsInt,
                djburger.validators.constructors.Lambda(key=lambda data: data > 0),
            ])
            v = v('4')
            self.assertFalse(v.is_valid())

    def test_or_validator(self):
        with self.subTest(src_text='or int pass'):
            v = djburger.validators.constructors.Or([
                djburger.validators.constructors.IsInt,
                djburger.validators.constructors.IsStr,
            ])
            v = v(4)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='or str pass'):
            v = djburger.validators.constructors.Or([
                djburger.validators.constructors.IsInt,
                djburger.validators.constructors.IsStr,
            ])
            v = v('lol')
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='or list not pass'):
            v = djburger.validators.constructors.Or([
                djburger.validators.constructors.IsInt,
                djburger.validators.constructors.IsStr,
            ])
            v = v([4, 5])
            self.assertFalse(v.is_valid())
