import requests
from bs4 import BeautifulSoup as bs





def main():
	"""
	url = "https://www.lyft.com/careers#openings"
	response = requests.get(url)

	with open("lyft.html", "wb") as f:
		f.write(response.content)
	"""

	with open("lyft.html","r",encoding="utf-8") as f:
		html_content = f.read()

	soup = bs(html_content, 'html.parser')
	print(soup)











if __name__ == "__main__":
	main()
