#Import libraries
import crawler_module

url = input("Please enter the URL - ").strip()
depth = int(input("Please enter the depth - "))

#Call functions from the imported modules
crawler_module.crawler(url, depth)
crawler_module.fetch_content()