import requests
from bs4 import BeautifulSoup
from mysql.connector import connect
from os import path

locations = []

#First web page
url = ('https://thegreatestbooks.org/')

if not path.exists('page1.html'):
    response = requests.get(url) # Download the page

    with open('page1.html', 'wb') as f:
        f.write(response.content) # Write page to a file

#Connect to database
cnx = connect(user='micah', password='password', database='wpmb')
cursor = cnx.cursor()
query = '''CALL ListBook(%s, %s, %s, %s, %s, %s);'''
with open('page1.html', 'rb') as f:
    page = f.read()
    soup = BeautifulSoup(page, features="html.parser")
    for h4 in soup.find_all('h4')[1:30]:  # Provide an argument for find_all()
        As = h4.find_all('a')
        title = As[0].text
        author = As[1].text
        print("Title: " + title + " Author: " + author)
        cursor.execute(query, [title, "5.20", '2018-01-01', author, "EN302", "johndoe"])
        cnx.commit()


cnx.close()
