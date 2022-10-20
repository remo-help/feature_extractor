# Feature Extractor

## General

This repository contains the following files:

* `feature_extractor.py` - The main script. The feature extractor.

* `tests.py` - The test script for the feature extractor.

* `test.csv` - A data file for testing.

The feature_extractor takes a .csv file containing sentences and returns all tokens with prepared features for further processing.

## Input and Output

The extractor takes a .csv file (or multiple .csv files) as input. Any input file needs to be of the following format: 

* The first column is entitled 'Id' and contains a sequence of numerical sentence-IDs
* The second column is entitled 'Sentence' and contains one sentence per row. For reference, check sentences.csv

The extractor output is a .json file that contains one JSON object per line. Each JSON object has the following structure:

```json
{"id": "<sentence_id>_<token_index>", 
 "token": "<token>", 
 "features": ["<list_of_tokens>","<list_of_pos_tags>"]}
```
The "id" is composed of the sentence ID and the index of the token in the sentence. 
"token" contains the token itself. 
"features" is a list of lists, containing x features containing all tokens and tags in the range of n-window, n+window, whereas n is the index of the token. This includes the following combinations for **both tokens and POS tags**:
* `n-1, n`
* `n, n+1`
* `n-1, n, n+1`
* `n-2, n-1, n`
* `n, n+1, n+2`
* `n-2, n-1, n, n+1, n+2`
* and so on

The `"features"` list contains two lists. `features[0]` contains the tokens, `features[1]` contains the respective POS tags.

## Example Usage

To run the extractor on a single file (for example "test.csv"), call:

    python feature_extractor.py --file test.csv --token_regex "poodle"

This will extract all mentions of "poodle" in the file you called. You can also specify
your regular expression in the `config.yaml` file. 

You can also call the extractor on an entire directory. It will operate on all .csv files in the directory. 
Be aware that this only works if the IDs in the files are sequential across the files. In other words, the last ID in the "Id" column in file 1 has to be n-1 and the first ID in file 2 has to be n.
Further, the files have to be labelled alphabetically inside the directory.

    python feature_extractor.py --dir [your path here]

## Parameters

The extractor can take a number of arguments, but it must minimally have either `file` or `--dir`specified. 
You can specify these parameters in `config.yaml`, or you can specify them as command line input.
Please be aware that any parameter specified in the command line will override the parameter's value in the config file.
These are the possible parameters:

* `--file FILENAME` If you only want to operate on a single file, specify the filename with this argument.
* `--dir DIRECTORY` This will operate on all .csv files in the specified directory. Be aware that this only works if the IDs in the files are sequential across the files. In other words the last ID in the "Id" column in file 1 has to be n-1 and the first ID in file 2 has to be n.
Further, the files have to be labelled alphabetically inside the directory.
* `--token_regex` You can specify a regular expression here for the kinds of tokens you are looking for.
* `--pos_regex` Here you can specify the POS tag you want your token to have. This can be left empty.
* `--outputfile OUTPUTFILENAME` Specify a custom name for your outputfile. Default = 'features.json'
* `--encoding ENCODING` Specify encoding for your outputfile. Default = 'utf-8'
* `--uncased` Call this to make all tokens lowercase. Disabled by default.
* `--window WINDOW-SIZE(INT)` Use this to expand the window size for feature extraction. For example: `--window 3`, will result in all n-3,n+3 features being extracted.
This feature is experimental. Be aware that unextractable (not present) features will be ignored by the program. Minimally the window must be 1 or higher.
* `--config` The path to a custom config file. Defaults to `config.yml`.

You can also call `python feature_extractor.py -h` to receive this information in your terminal.

## Tests

Call `python tests.py` to run unit tests on the feature_extractor. Failing a test will yield an error. Please run `python tests.py` before you commit changes to feature_extractor.py. Please note that `test.csv` has to be present in the directory for this test script to function.

## Requirements

Run `pip install -r requirements.txt` to auto-install requirements. Or open the file to see required packages.

## Notes

This script was written for Python 3.8.
If a feature is unextractable (because it does not exist), the extractor simply skips it.
