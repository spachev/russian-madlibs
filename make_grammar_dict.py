#! /usr/bin/python3

import requests
import sys
import argparse
import lxml.html
import re
import logging

PAREN_RE = re.compile(r".*\((.*)\).*")
logging.basicConfig(level=logging.DEBUG,  format='%(asctime)s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)

def get_url_for_word(word):
	return f"https://en.wiktionary.org/wiki/{word}"

def debug(msg):
	logger.info(msg)

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
	except Exception as e:
		debug(e)
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
		debug(words_with_gr)

