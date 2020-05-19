from django.test import TestCase
print('django test_1.py')
class MyTestCase1(TestCase):

    def test_1(self):
        print('test1')
        self.assertEqual(1,1)

    def test_5(self):
        print('test5')
        self.assertEqual(1,1)

if __name__ == "__main__":
    print(f'{__file__} has been imported')

