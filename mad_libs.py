import random
import sys
import json
import re

DELIM_RE = re.compile(r"[\s\.\?\!\,]+")
n_phrases = 15
def read_json(filename):
	with open(filename,'r') as fh:
		return json.load(fh)
def parse_grammar_lookup_file(filename):
	d = read_json(filename)
	return d["gr_dict"]
def parse_sub_map(filename,gr_dict):
	sub_map = read_json(filename)
	for i in range(0,len(sub_map)):
		if isinstance(sub_map[i], str):
			sub_map[i] = gr_dict[sub_map[i]]
	return sub_map
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
		pos = random.randrange(0,len(sub_arr))
		res.append(sub_arr[pos])
	return " ".join(res)
        
gr_dict = parse_grammar_lookup_file(sys.argv[1])
sub_map = parse_sub_map(sys.argv[2],gr_dict)
for j in range(0,n_phrases+1):
    phrase = mad_libs(sys.argv[3],sub_map)
    print(phrase)

