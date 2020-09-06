#Import libraries
import crawler_module
import suggest_url
print("Enter your choice - \n")
print("1. Fetch content and keywords of a URL and store the data")
print("2. Suggest a URL based on previous data\n")
choice = int(input())
if choice==1:
	url = input("Please enter the URL - ").strip()
	depth = int(input("Please enter the depth - "))

	#Call functions from the imported modules
	crawler_module.crawler(url, depth)
	crawler_module.fetch_content()
else:
	url = input("Please enter the URL - ").strip()
	suggest_url.suggest(url)


