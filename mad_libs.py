import random
import sys
import json
import re

DELIM_RE = re.compile(r"[\s\.\?\!\,]+")
n_phrases = 15
def parse_sub_map(filename):
    with open(filename,'r') as fh:
        return json.load(fh)
def mad_libs(phrase,sub_map):
    res = []
    words = DELIM_RE.split(phrase)
    len_sub_map = len(sub_map)
    len_words = len(words)
    if len(sub_map) != len(words):
        raise Exception("Length of phrase {} is not the same as entries in sub_map {}".format(len_words,len_sub_map))
    for i in range(0,len(words)):
        sub_arr = sub_map[i].copy()
        sub_arr.append(words[i])
        random.shuffle(sub_arr)
        res.append(sub_arr[0])
        
    return " ".join(res)
        
        
sub_map = parse_sub_map(sys.argv[1])
for j in range(0,n_phrases+1):
    phrase = mad_libs(sys.argv[2],sub_map)
    print(phrase)

