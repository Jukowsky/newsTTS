import requests
from bs4 import BeautifulSoup

def get_column_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    content_div = soup.find('div', class_='article-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = '\n'.join([p.text.strip() for p in paragraphs])
        return content
    return None

def get_daily_sabah_columns():
    url = "https://www.dailysabah.com/columns"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    columns_data = []
    for article_tag in soup.find_all('div', class_='article-card'):
        title_tag = article_tag.find('h3')
        author_tag = article_tag.find('div', class_='author-info')
        link_tag = article_tag.find('a', class_='card')

        if title_tag and author_tag and link_tag:
            title = title_tag.text.strip()
            author = author_tag.text.strip()
            link = link_tag['href']
            full_content = get_column_content(link)
            columns_data.append({
                'title': title,
                'author': author,
                'link': link,
                'content': full_content
            })
    return columns_data

if __name__ == "__main__":
    columns = get_daily_sabah_columns()
    for column in columns:
        print(f"Title: {column['title']}\nAuthor: {column['author']}\nLink: {column['link']}\nContent: {column['content']}\n---")


