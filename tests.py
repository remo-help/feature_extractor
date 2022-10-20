import unittest

import feature_extractor

# this is predefined output from using tokenize() on test.csv, if you change your tokenizer, you may need to make
# some changes here
output_dic = [{"Id": "103_2", "token": "tokenization", "features": [["do tokenization", "We do tokenization"], ["VBP VB",
                                                                  "PRP VBP VB"]]}]

#defining what the output should look like with a window size of 3
output_dic_window_3 = [{"Id": "101_4", "token": "poodle", "features": [["a poodle", "poodle called", "a poodle called",
                                                                     "has a poodle", "poodle called corgi",
                                                                     "has a poodle called corgi", "friend has a poodle"],
                                                                     ["DT NN", "NN VBN", "DT NN VBN", "VBZ DT NN",
                                                                     "NN VBN NN", "VBZ DT NN VBN NN", "NN VBZ DT NN"]]}]

class TestMethods(unittest.TestCase):
    def setUp(self):
        pass

    def test_strings_a(self):
        """
        Ensures the read_in function works
        """
        frame = feature_extractor.read_in_csv("test.csv")
        self.assertEqual(frame["Id"][0],101)
        self.assertEqual(frame["Sentence"][0],
                         "My friend has a poodle called corgi",
                         "The read_in() function is not working as expected.")

    def test_tokenizer(self):
        """
        Tests the Tokenizer, you can modify the tokenizer on line 55 of feature extractor.py
        """
        frame = feature_extractor.read_in_csv("test.csv")
        line = feature_extractor.tokenizer.tokenize(frame["Sentence"][0])
        self.assertEqual(line, ['My', 'friend', 'has', 'a', 'poodle', 'called', 'corgi'])


    def test_tags(self):
        """
        Tests the tagging, the relevant function is feature_extractor.tokenize_tag()
        """
        frame = feature_extractor.read_in_csv("test.csv")
        line = feature_extractor.tokenize_tag(frame["Sentence"][0])
        self.assertEqual(line, [('My', 'PRP$'), ('friend', 'NN'), ('has', 'VBZ'), ('a', 'DT'),
                                ('poodle', 'NN'), ('called', 'VBN'), ('corgi', 'NN')])


    def test_extraction(self):
        """
        Makes sure the main feature extractor works as intended.
        """
        frame = feature_extractor.read_in_csv("test.csv")
        output = feature_extractor.extractor(input=frame, lower=False, window=2, token="to", pos_regex='.')
        self.assertEqual(output, output_dic)


    def test_extraction_window(self):
        """
        Tests the experimental window feature.
        """
        frame = feature_extractor.read_in_csv("test.csv")
        output = feature_extractor.extractor(input=frame, lower=False, window=3, token='poodle')
        self.assertEqual(output,output_dic_window_3)








def testing():
    unittest.main()

if __name__ == '__main__':
    unittest.main()