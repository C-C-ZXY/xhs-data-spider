import time
import random
import re
import json
import gc
from DrissionPage import WebPage
from collections import defaultdict

FILTER_PATTERN = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]')

def filter_comments(comment):
    return re.sub(FILTER_PATTERN, '', comment)

def scrape_xhs_data():
    json_data_list = []
    wp = WebPage()
    wp.get('https://www.xiaohongshu.com/explore')
    wp.ele('xpath://section')
    wp.ele('xpath://div[@class="search-icon"]').click()
    wp.listen.start('api/sns/web/v1/feed')

    for index in range(100):
        if index in [9, 19, 31, 41, 53, 63, 75, 85, 97, 107]:
            continue
        try:
            wp.ele(f'xpath://section[@data-index="{index}"]').click()
            pack = wp.listen.wait()
            json_data = pack.response.body
            note = json_data['data']['items'][0]['note_card']
            data_dict = {
                'ID': note['note_id'],
                'Username': filter_comments(note['user']['nickname']),
                'Title': filter_comments(note['title']),
                'Content': filter_comments(note['desc']),
                'LikeCount': filter_comments(str(note['interact_info']['liked_count'])),
                'CollectCount': filter_comments(str(note['interact_info']['collected_count'])),
                'CommentCount': filter_comments(str(note['interact_info']['comment_count'])),
            }
            json_data_list.append(data_dict)
            print(data_dict)
            time.sleep(random.randint(2, 6))
            if len(json_data_list) >= 100:
                break
        except Exception as e:
            print(f"Error at index {index}: {e}")
    with open('XHS_data.json', mode='w', encoding='utf-8') as json_file:
        json.dump(json_data_list, json_file, ensure_ascii=False, indent=4)
    wp.quit()
    gc.collect()

if __name__ == "__main__":
    scrape_xhs_data()
