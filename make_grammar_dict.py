#! /usr/bin/python3

import requests
import sys
import argparse
import lxml.html
import re
import logging
import json
import os.path

PAREN_RE = re.compile(r".*\((.*)\).*")
def get_url_for_word(word):
	return f"https://en.wiktionary.org/wiki/{word}"

def debug(msg):
	logger.debug(msg)

def info(msg):
	logger.info(msg)

def save_out_file(out_file,out_dict):
	with open(out_file, "w") as fh:
		json.dump(out_dict, fh, indent=2)

def load_out_file(out_file):
	with open(args.lookup_out_file, "r") as fh:
		return json.load(fh)

def extract_gr_changes(root):
	cols = [el.text_content().strip() for el in root.xpath("//div[@class='NavContent']//tr[1]//th")
						if el.text_content().strip() ]
	rows = [el.text_content().strip() for el in root.xpath("//div[@class='NavContent']//tr//th[1]")
						if el.text_content().strip() ]
	gr_lookup = {}
	for r_ind in range(0, len(rows)):
		c_ind_offset = 0
		for c_ind in range(0, len(cols)):
			gr_ident = f"{rows[r_ind]}|{cols[c_ind]}"
			word_xpath_td = f"//div[@class='NavContent']//tr[{r_ind+2}]/td[{c_ind+1-c_ind_offset}]"
			word_xpath = word_xpath_td + "/span[1]"
			debug(word_xpath)
			word = root.xpath(word_xpath)[0].text_content().strip()
			td_el = root.xpath(word_xpath_td)[0]
			colspan = int(td_el.get("colspan", 1))
			c_ind_offset += colspan - 1
			debug(f"{gr_ident} : {word}")
			gr_lookup[gr_ident] = word
	return gr_lookup

def get_grammar(word):
	url = get_url_for_word(word)
	debug(url)
	rsp = requests.get(url,timeout=2)
	if not rsp.ok:
		return None
	root = lxml.html.fromstring(rsp.content)
	gr_changes = None
	try:
		gr_els = root.xpath('//h2[span[@id="Russian"]]/following-sibling::div//div[@class="NavHead"]')
		gr_txt = gr_els[0].text_content().strip()
		m = PAREN_RE.match(gr_txt)
		if not m:
			return None
		gr_txt = m.group(1)
		gr_changes = extract_gr_changes(root)
	except Exception as e:
		debug(e)
		return None
	return {"word": word, "gr": gr_txt, "gr_changes" : gr_changes}

parser = argparse.ArgumentParser(description='Build a Russian grammar dictionary')
parser.add_argument('--input-file', help='Dictionary source file', required=True)
parser.add_argument('--max-words', help='Maximum words to scrape', default=None)
parser.add_argument('--lookup-out-file', help='Output file for loookup', required=True)
parser.add_argument('--debug', action='store_true', help='Which level to log')
parser.add_argument('--save-file-frequency', help='How often to save to out file', default=10)

args = parser.parse_args()
gr_dict = {}
out_dict = {'cur_line' : 0}
n_words = 0
max_words = None
debug_level = logging.INFO
save_frequency = None

if args.max_words:
	max_words = int(args.max_words)

if args.debug:
	debug_level = logging.DEBUG

if args.save_file_frequency:
	save_frequency = int(args.save_file_frequency)

logging.basicConfig(level=debug_level,  format='%(asctime)s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)
n_lines = 0

if os.path.exists(args.lookup_out_file):
	out_dict = load_out_file(args.lookup_out_file)
	n_words = out_dict["n_words"]

with open(args.input_file, 'r') as fh:
	n_requests = 0
	for l in fh:
		n_lines += 1
		if n_lines <= out_dict['cur_line']:
			continue
		parts = l.split("/")
		if len(parts) != 2:
			continue
		n_requests += 1
		words_with_gr = get_grammar(parts[0])
		if words_with_gr is None:
			continue
		debug(words_with_gr)
		for k,v in words_with_gr['gr_changes'].items():
			gr_k = words_with_gr['gr'] + "|" + k
			if gr_k not in gr_dict:
				gr_dict[gr_k] = []
			gr_dict[gr_k].append(v)
		n_words += 1
		info(f"Number of requests : {n_requests}, Number of words {n_words}")
		out_dict = {'cur_line' : n_lines, 'n_requests' : n_requests,'n_words' : n_words, 'gr_dict' : gr_dict}
		if n_words % save_frequency == 0:
			save_out_file(args.lookup_out_file,out_dict)
		if max_words and n_words == max_words:
			break

save_out_file(args.lookup_out_file,out_dict)
