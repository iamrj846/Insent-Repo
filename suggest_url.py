#Import libraries
import requests
from urllib.request import urlparse, urljoin
from bs4 import BeautifulSoup
from gensim.summarization import keywords
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer
import crawler_module

def is_valid(url):
   parsed = urlparse(url)
   return bool(parsed.netloc) and bool(parsed.scheme)

def suggest(url):
	if is_valid(url):
		#Extract text from HTML tags
		page = requests.get(url).text
		soup = BeautifulSoup(page, features="lxml")    
		p_tags = soup.find_all('p')
		h1_tags = soup.find_all('h1')
		h2_tags = soup.find_all('h2')
		h3_tags = soup.find_all('h3')
		h4_tags = soup.find_all('h4')
		p_tags_text = [tag.get_text().strip() for tag in p_tags]

		#Performed text cleaning here
		sentence_list = [sentence for sentence in p_tags_text if not '\n' in sentence]
		sentence_list = [sentence for sentence in sentence_list if '.' in sentence]
		article = ""
		for i in range(0, len(sentence_list)):
			article = article + sentence_list[i] + " "


		h1_tags_text = [tag.get_text().strip().replace("\n", " ") for tag in h1_tags]
		h2_tags_text = [tag.get_text().strip().replace("\n", " ") for tag in h2_tags]
		h3_tags_text = [tag.get_text().strip().replace("\n", " ") for tag in h3_tags]
		h4_tags_text = [tag.get_text().strip().replace("\n", " ") for tag in h4_tags]

		article_for_keywords = article + " ".join(h1_tags_text) + " ".join(h2_tags_text) + " ".join(h3_tags_text) + " ".join(h4_tags_text)

		#generated keywords here. 20 keywords each for a URL, with their scores and also performed lemmatization.
		key_words = crawler_module.keyword_gen(article_for_keywords)
		joined_keyword = " ".join(key_words)
		
		f = open(f"data.txt", "r")
		url_with_score = []
		for line in f:
			line_tokenize = word_tokenize(line)
			joined_keyword_tokenize = word_tokenize(joined_keyword)
			line_set = set(line_tokenize)
			joined_set = set(joined_keyword_tokenize)
			rvector = line_set.union(joined_set)
			l1 = []
			l2 = []
			for w in rvector: 
			    if w in line_set:
			    	l1.append(1) # create a vector 
			    else: 
			    	l1.append(0) 
			    if w in joined_set:
			    	l2.append(1) 
			    else:
			    	l2.append(0) 
			c = 0
			# cosine formula  
			for i in range(len(rvector)): 
			    c+= l1[i]*l2[i] 
			cosine = c / float((sum(l1)*sum(l2))**0.5)
			url_with_score.append([line.split(",")[0].strip(), cosine])
		print("\n")
		for l in url_with_score:
			print(f"{l[0]} ==> {l[1]}")

		print("\n\n\n")
		max_score = 0
		chosen_one = ""
		for l in url_with_score:
			if(l[1]>max_score):
				max_score = l[1]
				chosen_one = l[0]
		print(f"=============================================================\n{chosen_one} --- has similarity score {max_score}")
	else:
		print("Invalid URL")