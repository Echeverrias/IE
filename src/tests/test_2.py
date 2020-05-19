from django.test import TestCase
print('django test_1.py')
class MyTestCase2(TestCase):

   def test_2(self):
       print('test2')
       self.assertEqual(1,1)

   def test_3(self):
       print('test3')
       self.assertEqual(1, 1)

if __name__ == "__main__":
    print(f'{__file__} has been imported')

