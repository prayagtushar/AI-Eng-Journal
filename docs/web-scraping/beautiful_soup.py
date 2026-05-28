from bs4 import BeautifulSoup

soup = BeautifulSoup("https://www.ycombinator.com/companies", "lxml")

# By the tag and class
title = soup.find("h2", class_="company-name").get_text(strip=True)

# BY CSS
desc = soup.select_one("div.company-desc p").get_text(strip=True)

# All the matches
founder = [a.get_text(strip=True) for a in soup.select("ul.founders li a")]

url = soup.find("a", string="website")["href"]
