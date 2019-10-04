# -*- coding: utf-8 -*-
import argparse
import json
import os
import shutil
import sys
from multiprocessing.dummy import Pool as ThreadPool
from zipfile import ZipFile

import textract
from cleantext import clean


# from tqdm import tqdm

# rpm -ivh https://forensics.cert.org/centos/cert/7/x86_64//antiword-0.37-9.el7.x86_64.rpm


class datastructure(object):
    """
    datastructure will save the information related to a document
    """

    def __init__(self, filename, data):
        self.filename = filename
        self.data = data
        self.words = []

    def dump(self):
        return json.dumps(self.__dict__)


def parse_core(file):
    struct = None
    try:
        # Extract text
        text = extract_text(file)
        # Remove root path
        _path = "/".join(file.split("/")[1:])
        struct = datastructure(_path, text)
    except KeyboardInterrupt:
        print("EXIT!")
        sys.exit()
    except Exception:
        extension = os.path.splitext(file)[1]
        print("ERROR! File {} | Error: {} not supported".format(file, extension))
    return struct


def parse(path, outputFile):
    print("Loading files from {} ...".format(path))
    # Loading data into a datastructure and saving into a list
    data = []
    files = retrieveFile(path)
    if len(files) == 0:
        print("Empty data!")
        return

    pool = ThreadPool(6)
    data = pool.map(parse_core, files)
    data = list(filter(None.__ne__, data))  # Remove None
    # for file in tqdm(files, mininterval=0.5, desc="Extracting text ...",total=len(files)):
    #     try:
    #         # Extract text
    #         text = extract_text(file)
    #         # Remove root path
    #         _path = "/".join(file.split("/")[1:])
    #         struct = datastructure(_path, text)
    #         data.append(struct)
    #     except KeyboardInterrupt:
    #         print("EXIT!")
    #         sys.exit()
    #     except Exception:
    #         extension = os.path.splitext(file)[1]
    #         print("ERROR! File {} | Error: {} not supported".format(file, extension))

    print("Removing unzipped data")
    shutil.rmtree(path)

    print("Loaded {} files from {} ... Saving unique words ...".format(
        len(data), len(files)))

    # Saving unique words
    for item in data:
        words = set()
        for word in item.data.split(" "):
            words.add(word)
        item.words = list(words)

    print("Unique words saved, dumping JSON data")
    with open(outputFile, "w") as f:
        f.write("[")
        f.writelines(",".join([x.dump() for x in data]))
        f.write("]")
    print("JSON data dumped ")



def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', default='dataset.txt', dest='dataset_output',
                        help='Output JSON file')
    parser.add_argument('-u', action='store', default='http://0.0.0.0:8082/GoDocData.zip',
                        dest='URL', help='Output JSON file')
    results = parser.parse_args()
    print("Output File: {} URL: {}".format(
        results.dataset_output, results.URL))
    return results.dataset_output, results.URL


def extract_text(file):
    text = str(textract.process(file))
    text = clean(text, fix_unicode=True, to_ascii=True, lower=False, no_line_breaks=True, no_punct=True)
    return text.replace('"', "'").replace("|", "")


# Return the lits of file contained in all subdirectory
def retrieveFile(path):
    files = set()
    if not os.path.isdir:
        print("Error! {} is not a folder!".format(path))
        return None
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            files.add(os.path.join(dirpath, filename))
    print("Path {} have {} files".format(path, len(files)))
    return list(files)


def unzip_file(path):
    extractPath = "/".join(path.split("/")[:-1])
    print("Unzipping files ... {}".format(extractPath))
    with ZipFile(path) as zip_ref:
        zip_ref.extractall(extractPath)
    print("Files unzipped! ...")
    return extractPath + "/" + path.split("/")[-1].replace(".zip", "")
