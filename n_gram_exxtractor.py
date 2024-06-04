
import pandas as pd
import argparse
import re
import os
import json
import yaml
from collections import Counter



# This is our read in function for .csv files. If you need to change any parameters of pd.read_csv (such as delimiter type)
# be aware that those changes will be global
# Options for pd.read_csv: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
# takes a string (path) and returns a pd.DataFrame
def read_in_csv(path: str) -> pd.DataFrame:
    """Takes a path string and returns a DataFrame.

    Args:
        path (str): The path to a .csv file

    Returns:
        DataFrame: The .csv file as a DataFrame
    """
    file = pd.read_csv(path)
    return file


# This is our argument parser. We're defining it outside of main() for convenience purposes.
# Here we can add command line arguments.
def start_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Extracts sentences from a .csv file (please see readme for required '
                                                 'format). Tokenizes and POS tags them. '
                                                 'In order to run unit tests, call tests.py')
    parser.add_argument("--config",
                        help="The path to your config file. You can manually override params you specify in config.",
                        required=False, default='config.yaml')
    parser.add_argument("--file",
                        help="The path to the file you wish to process. If you want to batch process files, "
                             "please use the --dir argument.",
                        required=False)
    parser.add_argument("--token_regex",
                        help="The regex for the tokens you are looking for",
                        required=False)
    parser.add_argument("--pos_regex",
                        help="The regex for the POS tags you are looking for.",
                        required=False)
    parser.add_argument("--outputfile",
                        help="The name of your outputfile. Default: features.json",
                        required=False)
    parser.add_argument("--encoding",
                        help="The encoding of your outputfile. Default: utf-8",
                        required=False, default="utf-8")
    parser.add_argument("--dir", help="The path to the directory you wish to process. "
                                      "This will run the extraction on ALL .csv files in the directory "
                                      "in sequential order and output the results in ONE file. "
                                      "Please make sure your .csv files have unique and continuous ID columns",
                        required=False)
    parser.add_argument("--window", help="The window-size for feature extractions. "
                                         "By default the extractor looks at a window of n-2,n+2 while n is the token."
                                         " This can be set higher or lower. Minimum:1, Default:2",
                        required=False, type=int)
    parser.add_argument("--uncased",
                        help="If activated, the tokenizer will return uncased (all lower case) tokens."
                             "This is off by default",
                        required=False, action='store_true')
    parser.add_argument("--count",
                        help="marks whether we export a count of ngrams",
                        required=False, action='store_true')
    return parser




def tokenize_tag(sentence: str, uncase: bool=False)->[()]:
    """Takes a sentence string and returns a list of tag Tuples.

    Args:
        sentence (str): The sentence to be processed
        uncase (bool): A flag used to decide whether to .lower() the sentence

    Returns:
        list: a list of tag Tuples
    """
    if uncase:
        sentence = sentence.lower()
    tokens = sentence.split()

    return tokens




# This function does the bulk amount of work. It takes a pd.DataFrame as input and returns a list of dictionaries.
# It also has a window option that allows you to expand the feature window
# Each dictionary has the following values {Id:token ID, token: token, features: [list of features]}
# We can later export this list of dictionaries as JSON objects and write them into a file.
def extractor(input: pd.DataFrame, token_pattern: str, lower: bool=False, window: int=2, count: bool=False) -> [dict]:
    """Takes a DataFrame and returns a list of dictionaries.

    Args:
        count: whether to export a count of all found n_grams
        input (pd.DataFrame): A a DataFrame containing sentences and sentence IDs
        lower (bool): A flag for lowercasing the tokens
        window (int): A flag for setting the window size (experimental feature)

    Returns:
        A list of dictionaries. Each Dictionary contains an ID, a token, and a list of features.
    """
    # first we define the output list
    feature_list = []
    # now we start the main loop, this iterates over all indices of the DataFrame
    for i in input.index:
        # For each sentence we define the numerical sentence-ID
        Id = input['Id'][i]
        # creating a list of tokens for each sentence, starting with pulling the sentence as a string
        sentence = input['Sentence'][i]
        # in case --uncased is activated, lower will be True, then we will lowercase all tokens, we let "lower"
        # be inherited into the tokenize function
        tokens = tokenize_tag(sentence, lower)
        # iterating over our list of tags, tags are tuples, this part gets messy
        for index in range(0, len(tokens)):
            # here we select the tuple we want to look at
            token = tokens[index]
            # filtering for the tokens we are looking for. This is written in a bit of a messy way,
            # but here is a quick summary on this condition:
            # If there is a specified & found and we have one of the tokens specified in the token_regex,
            # then we trigger.
            if re.match(token_pattern, token):
                    #and tags[tuple_index+1][1][0] !="V":
                # in this list we will keep all features associated with the tuple we have selected for operation
                all_features = []
                pos_features = []
                token_features = []
                # the index of this tuple is the same as the position in the range, but we redefine them here regardless
                # now we add all n-1,n+2 tokens.
                # We save these and then recursively iterate over them according to window size.
                # try/except conditions are here so system does not fail if no features present
                if index + window < len(tokens)+1:
                    for i in range(window):
                        idx = index + i
                        token_features.append(tokens[idx])
                else:
                    t = index + window
                    j = len(tokens)+1
                    overshoot = t - j
                    for i in range(window-overshoot):
                        idx = index + i
                        token_features.append(tokens[idx])

            else:
                continue
            # We make sure that we are not exporting an empty list
            if token_features:
                all_features = token_features
                # The ID is a combination of the sentence ID and the index of the token in the token list
                token_id = str(Id) + '_' + str(index)
                # This is the structure of our dictionaries. Each token is stored as a dictionary
                temp_dic = {"Id": token_id, "token": tokens[index], f"{window}_gram": all_features}
                feature_list.append(temp_dic)
    # Returning the list of dictionaries
    n_gram_list = [" ".join(i[f"{window}_gram"]) for i in feature_list]
    if count:
        print(n_gram_list)
        n_count = Counter(n_gram_list)
        return feature_list, n_count
    else:
        return feature_list




##########################################

# Here we define our export function.
# It takes a list of dictionaries and a filename and produces a file of JSON objects, it has an option for encoding.
def export(features: [dict], filename: str, encod= str("utf-8"), count: bool=False):
    """Takes a list of dictionaries and writes the dictionaries as JSON objects in a file.

    Args:
        features [dict]: A list of dictionaries
        filename (str): The filename of your file
        encod (str): Encoding of your file

    Returns:
        nothing, but writes a file
    """
    # opening our file, beware that "w+" will overwrite
    # Now we dump a json for every entry in our dictionary list.
    print(features)
    if count:
        #features = features[0]
        #ngrams = features[1]
        features, ngrams = features
        writefile = open(filename+'n_gram_count', "w+", encoding=encod)
        # Now we dump a json for every entry in our dictionary list.
        for i in ngrams:
            writefile.write(f"{i}:{ngrams[i]}")
            if (len(features) - 1) > features.index(i):
                writefile.write("\n")
        writefile.close()
        for i in features:
            json.dump(i, writefile)
            if (len(features) - 1) > features.index(i):
                writefile.write("\n")
        writefile.close()
    else:
        writefile = open(filename, "w+", encoding=encod)
        for i in features:
            json.dump(i, writefile)
            if (len(features) - 1) > features.index(i):
                writefile.write("\n")
        writefile.close()
# This is the function for exporting to a single file from multiple .csv files.
# It takes a list of lists of dictionaries and producs a file with JSON objects.
def export_multiple(list_of_features: [[dict]], filename: str, encod= str("utf-8"), count:bool=False):
    """Takes a list of lists dictionaries and writes the dictionaries as JSON objects in a file.

    Args:
        features [[dict]]: A list of lists of dictionaries
        filename (str): The filename of your file
        encod (str): Encoding of your file

    Returns:
              nothing, but writes a file
    """
    # opening our file, beware that "w+" will overwrite
    writefile = open(filename, "w+", encoding=encod)
    # iterating over the list of lists, each list inside the list contains the features of one file
    for features in list_of_features:
        # Now we dump a json for every entry in our dictionary list.
        for i in features:
            json.dump(i, writefile)
            if (len(features) - 1) > features.index(i):
                writefile.write("\n")
    writefile.close()

# we define a class here that allows us to turn a dictionary into a namespace, we need this to override the config later
class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def main() -> None:
    # parse our commandline arguments
    parser = start_parser()
    arguments = parser.parse_args()
    # we get the namespace as a dictionary so we can iterate
    arg_dict = arguments.__dict__
    # we load the config file
    with open(arguments.config, 'r') as file:
        config = yaml.safe_load(file)
    # now we override all config file entries with the entries from the commandline args
    for key in arg_dict:
        if arg_dict[key]:
            config[key] = arg_dict[key]

    args = Config(**config)
    args.count == True if args.count else False

    if args.file and not args.dir:
        file = read_in_csv(args.file)
        if args.uncased:
            tokens = extractor(file, token_pattern=args.token_regex, lower=True, window=args.window, count=args.count)
        else:
            tokens = extractor(file, lower=False, window=args.window, token_pattern=args.token_regex, count=args.count)
        export(features=tokens,filename=args.outputfile,encod=args.encoding, count=args.count)
        print("success")
    elif args.dir and not args.file:
        print("operating on the directory you specified")
        # this is where we will store the outputs from different files
        list_of_lists=[]
        for entry in os.scandir(args.dir):
            if entry.path.endswith(".csv") and entry.is_file():
                filename = entry.path
                file = read_in_csv(filename)
                if args.uncased:
                    tokens = extractor(file, token_pattern=args.token_regex,
                                       lower=True, window=args.window)
                else:
                    tokens = extractor(file, token_pattern=args.token_regex,
                                       lower=False, window=args.window)
                list_of_lists.append(tokens)
        print("success")
        export_multiple(list_of_features=list_of_lists, filename=args.outputfile, encod=args.encoding)



    else:
        print("Pleas try -h for help. Please specify either --file or --dir arguments in your config file or"
              "in your command line to run")


if __name__ == '__main__':
    main()
