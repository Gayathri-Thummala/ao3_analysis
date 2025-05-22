import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

class AO3BasicScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_fandom_works(self, fandom_tag, max_pages=5, output_file='queen_of_tears_AO3_data.csv'):
        """
        Scrape basic work information from AO3 for a specific fandom
        """
        works_data = []

        for page in range(1, max_pages + 1):
            print(f"Scraping page {page}...")

            # Construct URL for fandom search
            url = f"https://archiveofourown.org/tags/{fandom_tag}/works"
            params = {
                'page': page,
                'work_search[sort_column]': 'revised_at'  # Sort by recently updated
            }

            try:
                # Increase delay to avoid rate limiting
                time.sleep(10)  # Increased from 2 to 5 seconds

                response = self.session.get(url, params=params)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all work items - try multiple selectors
                works = soup.find_all('li', class_='work blurb group')
                if not works:
                    # Alternative selector
                    works = soup.find_all('li', class_='work')

                print(f"Found {len(works)} works on page {page}")

                if len(works) == 0:
                    print("No works found on this page, skipping...")
                    continue

                for work in works:
                    work_data = self.extract_work_info(work)
                    if work_data:
                        works_data.append(work_data)

                # Save data incrementally after each page
                df = pd.DataFrame(works_data)

                # Append data to CSV and write header only for the first page
                df.to_csv(output_file, index=False, mode='a', header=(page == 1))
                print(f"✓ Saved data for page {page} to {output_file}")

            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue

        print(f"✓ Finished scraping {len(works_data)} works in total.")
        return pd.DataFrame(works_data)

    def extract_work_info(self, work_element):
        """
        Extract information from a single work element
        """
        try:
            # Title and URL - more robust extraction
            title_element = work_element.find('h4', class_='heading')
            if not title_element:
                title_element = work_element.find('h4')

            title = 'Unknown'
            work_url = ''
            if title_element:
                link = title_element.find('a')
                if link:
                    title = link.get_text(strip=True)
                    work_url = link.get('href', '')

            # Author - more robust extraction
            author_element = work_element.find('a', rel='author')
            if not author_element:
                author_element = work_element.find('a', {'rel': 'author'})
            author = author_element.get_text(strip=True) if author_element else 'Anonymous'

            # Stats extraction - improved
            stats = {'kudos': 0, 'comments': 0, 'bookmarks': 0, 'hits': 0}

            # Try different ways to find stats
            stats_element = work_element.find('dl', class_='stats')
            if stats_element:
                for dd in stats_element.find_all('dd'):
                    classes = dd.get('class', [])
                    text = dd.get_text(strip=True).replace(',', '')

                    if text.isdigit():
                        value = int(text)
                        if 'kudos' in classes:
                            stats['kudos'] = value
                        elif 'comments' in classes:
                            stats['comments'] = value
                        elif 'bookmarks' in classes:
                            stats['bookmarks'] = value
                        elif 'hits' in classes:
                            stats['hits'] = value

            # Tags
            tags_element = work_element.find('ul', class_='tags commas')
            tags = []
            if tags_element:
                for tag in tags_element.find_all('a', class_='tag'):
                    tags.append(tag.text.strip())

            # Publication date
            date_element = work_element.find('p', class_='datetime')
            pub_date = date_element.text.strip() if date_element else 'Unknown'

            # Word count
            word_count = 0
            words_element = work_element.find('dd', class_='words')
            if words_element and words_element.text.strip():
                word_count = int(words_element.text.strip().replace(',', ''))

            return {
                'title': title,
                'author': author,
                'url': 'https://archiveofourown.org' + work_url if work_url else '',
                'kudos': stats.get('kudos', 0),
                'comments': stats.get('comments', 0),
                'bookmarks': stats.get('bookmarks', 0),
                'hits': stats.get('hits', 0),
                'tags': ', '.join(tags),
                'publication_date': pub_date,
                'word_count': word_count
            }

        except Exception as e:
            print(f"Error extracting work info: {e}")
            return None


# Example usage for Queen of Tears K-drama analysis
if __name__ == "__main__":
    scraper = AO3BasicScraper()

    # Queen of Tears fandom tag from the URL you provided
    fandom = "%EB%88%88%EB%AC%BC%EC%9D%98%20%EC%97%AC%EC%99%95%20%7C%20Queen%20of%20Tears%20(TV)"

    print("Starting Queen of Tears fanfiction analysis...")

    # Start with 5 pages to scrape more data and avoid rate limiting
    df = scraper.scrape_fandom_works(fandom, max_pages=5)

    if len(df) > 0:
        print(f"✓ Successfully collected {len(df)} Queen of Tears fanfictions")
    else:
        print("❌ No works found. You may need to adjust the fandom tag.")
        print("Go to AO3, search for 'Queen of Tears', and copy the exact tag format from the URL.")
