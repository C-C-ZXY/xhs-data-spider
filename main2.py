import time
import random
import re
import json
import gc
from DrissionPage import WebPage
from collections import defaultdict

class XHSScraper:
    FILTER_PATTERN = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]')

    def __init__(self, output_filename='XHS_data.json'):
        self.output_filename = output_filename
        self.scraped_data = []
        self.page = WebPage()

    def _filter_text(self, text):
        return re.sub(self.FILTER_PATTERN, '', str(text))

    def _initialize_browser(self):
        self.page.get('https://www.xiaohongshu.com/explore')
        self.page.ele('xpath://section')
        self.page.ele('xpath://div[@class="search-icon"]').click()
        self.page.listen.start('api/sns/web/v1/feed')

    def _process_post(self, packet):
        try:
            json_data = packet.response.body
            note = json_data['data']['items'][0]['note_card']
            data_dict = {
                'ID': note['note_id'],
                'Username': self._filter_text(note['user']['nickname']),
                'Title': self._filter_text(note['title']),
                'Content': self._filter_text(note['desc']),
                'LikeCount': self._filter_text(note['interact_info']['liked_count']),
                'CollectCount': self._filter_text(note['interact_info']['collected_count']),
                'CommentCount': self._filter_text(note['interact_info']['comment_count']),
            }
            self.scraped_data.append(data_dict)
            print(data_dict)
            return True
        except Exception as e:
            print(f"Error processing post data: {e}")
            return False

    def scrape(self, max_posts=100):
        self._initialize_browser()
        indices_to_skip = {9, 19, 31, 41, 53, 63, 75, 85, 97}

        index = 0
        while len(self.scraped_data) < max_posts:
            if index in indices_to_skip:
                index += 1
                continue
            try:
                self.page.ele(f'xpath://section[@data-index="{index}"]').click()
                pack = self.page.listen.wait()
                self._process_post(pack)
                time.sleep(random.randint(2, 6))
            except Exception as e:
                print(f"Error at index {index}: {e}")
            
            index += 1
            if index > max_posts + len(indices_to_skip): # Failsafe to prevent infinite loops
                print("Exceeded maximum search index.")
                break


    def save_to_json(self):
        with open(self.output_filename, mode='w', encoding='utf-8') as json_file:
            json.dump(self.scraped_data, json_file, ensure_ascii=False, indent=4)
        print(f"\nData successfully saved to {self.output_filename}")

    def close(self):
        self.page.quit()
        gc.collect()

if __name__ == "__main__":
    scraper = XHSScraper(output_filename='XHS_data.json')
    try:
        scraper.scrape(max_posts=100)
        scraper.save_to_json()
    finally:
        scraper.close()
