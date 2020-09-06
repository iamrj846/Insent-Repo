#Import libraries
import requests
from urllib.request import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
from gensim.summarization import keywords
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer

#All the links with the same domain name as th input URL will be stored
#in internal_links set and others in external_links set

internal_links = set()
external_links = set()

#I have used colorama just for using different colors when printing, to distinguish between internal and external links
colorama.init()
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
RESET = colorama.Fore.RESET

#This method checks for the validity of the URL
def is_valid(url):
   parsed = urlparse(url)
   return bool(parsed.netloc) and bool(parsed.scheme)


#This method retrieves all the URLs inside a given URL and stores it in
#internal_links and external_links separately

def get_all_website_links(url):
   urls = set()
   domain_name = urlparse(url).netloc
   soup = BeautifulSoup(requests.get(url).content, "html.parser")
   for a_tag in soup.findAll("a"):
      href_tag = a_tag.attrs.get("href")
      if href_tag=="" or href_tag==None:
         continue
      href_tag = urljoin(url, href_tag)
      parsed_href = urlparse(href_tag)
      href_tag = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

      #If the link is not valid, we don't consider it.
      if not is_valid(href_tag):
         continue

      #If the link has already been accessed before, we ignore it.
      if href_tag in internal_links:
         continue

      #If the domain name of the input link does not match with the link, it belongs to external_links
      if domain_name not in href_tag:
         if href_tag not in external_links:
            print(f"{RED}[!] External link: {href_tag}{RESET}")
            external_links.add(href_tag)
         continue

      #Else, we add it to internal_links
      urls.add(href_tag)
      internal_links.add(href_tag)
      print(f"{GREEN}[*] Internal link: {href_tag}{RESET}")
   return urls

#This method is used to crawl an input link upto a particular depth.
def crawl(url, depth):
   if(depth==0):
      print(f"{GREEN}[*] Internal link: {url}{RESET}")
   elif(depth==1):
      get_all_website_links(url)
   else:
      #I have used a BFS approach considering the structure as a tree. It uses a queue based approach to traverse
      #links upto a particular depth.
      queue = []
      queue.append(url)
      for _ in range(depth):
         for count in range(len(queue)):
            url = queue.pop(0)
            urls = get_all_website_links(url)
            for i in urls:
               queue.append(i)

#This method is the driver method and takes url and depth as input and performs crawling and saves the results in 
#two files where internal_links and external_links are stored

def crawler(url, depth=1):
   domain_name = urlparse(url).netloc

   crawl(url, depth)

   print("Total Internal Links:", len(internal_links))
   print("Total External Links:", len(external_links))
   print("Total URLs:", len(external_links) + len(internal_links))

   with open(f"{domain_name}_internal_links.txt", "w") as f:
      for internal_link in internal_links:
         print(internal_link.strip(), file=f)
   with open(f"{domain_name}_external_links.txt", "w") as f:
      for external_link in external_links:
         print(external_link.strip(), file=f)


#This method is used to find keywords after tokenizing, stemming the tokens, and using weighted frequency to calculate scores

def keyword_gen(article):
   stop_words = set(stopwords.words('english'))
   word_tokens = word_tokenize(article)
   ps = PorterStemmer() 
   tokens = []
   filter_string = "@!~`#$%^&*_-:;.,/?|"
   for w in word_tokens:
      if w not in stop_words and w not in filter_string:
         tokens.append(ps.stem(w))
   article_for_keywords = " ".join(tokens)
   key_words = keywords(article_for_keywords, words=20, split=True, scores=False, pos_filter=('NN'), lemmatize=True, deacc=True)
   return key_words

#This method is used to fetch content from the set of internal links. Fetched all the text in paragraph tags, 
# H1 and H2 header tags.

def fetch_content():
   for url in internal_links:
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

      #generated keywords here. 10 keywords each for a URL, with their scores and also performed lemmatization.
      key_words = keyword_gen(article_for_keywords)

      print(url.strip())
      print()
      print("Text in Paragraphs is - \n")
      print(article)
      print()
      print("H1 tags are - \n")
      print(h1_tags_text)
      print()
      print("H2 tags are - \n")
      print(h2_tags_text)
      print()
      print("H3 tags are - \n")
      print(h3_tags_text)
      print()
      print("H4 tags are - \n")
      print(h4_tags_text)

      print("\nThe keywords are - ")
      print(key_words)
      print("--------------------------------------------------\n")

      #Stored the results in a file
      with open(f"html_internal_links.txt", "a+") as f:
         print(url.strip(), file=f)
         print(file=f)
         print("Text in Paragraphs is - \n", file=f)
         print(article, file=f)
         print(file=f)
         print("H1 tags are - \n", file=f)
         print(h1_tags_text, file=f)
         print(file=f)
         print("H2 tags are - \n", file=f)
         print(h2_tags_text, file=f)
         print(file=f)
         print("H3 tags are - \n", file=f)
         print(h3_tags_text, file=f)
         print(file=f)
         print("H4 tags are - \n", file=f)
         print(h4_tags_text, file=f)
         print("\nThe keywords are - \n", file=f)
         print(key_words, file=f)
         print("--------------------------------------------------\n", file=f)

      joined_key_words = " ".join(key_words)
      with open(f"data.txt", "a+") as f:
         print(f"{url.strip()} , {joined_key_words}", file=f)






