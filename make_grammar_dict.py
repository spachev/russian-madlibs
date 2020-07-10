#! /usr/bin/python3

import requests
import sys
import argparse
import lxml.html
import re

PAREN_RE = re.compile(r".*\((.*)\).*")

def get_url_for_word(word):
	return f"https://en.wiktionary.org/wiki/{word}"

def extract_gr_changes(root):
	cols = [el.text_content().strip() for el in root.xpath("//div[@class='NavContent']//tr[1]//th")
						if el.text_content().strip() ]
	print(cols)

def get_grammar(word):
	url = get_url_for_word(word)
	print(url)
	rsp = requests.get(url)
	if not rsp.ok:
		return None
	root = lxml.html.fromstring(rsp.content)
	try:
		gr_els = root.xpath('//h2[span[@id="Russian"]]/following-sibling::div//div[@class="NavHead"]')
		gr_txt = gr_els[0].text_content().strip()
		m = PAREN_RE.match(gr_txt)
		if not m:
			return None
		gr_txt = m.group(1)
		extract_gr_changes(root)
	except:
		return None
	return {"word": word, "gr": gr_txt}

parser = argparse.ArgumentParser(description='Build a Russian grammar dictionary')
parser.add_argument('--input-file', help='Dictionary source file', required=True)
args = parser.parse_args()

with open(args.input_file, 'r') as fh:
	for l in fh:
		parts = l.split("/")
		if len(parts) != 2:
			continue
		words_with_gr = get_grammar(parts[0])
		if words_with_gr is None:
			continue
		print(words_with_gr)

