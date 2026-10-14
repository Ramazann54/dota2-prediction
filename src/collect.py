import os
import requests 
import json
import time
import logging

os.makedirs('data/raw', exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

URL = 'https://api.opendota.com/api/publicMatches'
PATH = 'data/raw/public_matches.jsonl'

def fetch_batch(less_than_id):
    """Делает один запрос к API OpenDota для получения матчей с match_id меньше less_than_id.
   Возвращает список матчей, [] если матчей больше нет, или None при ошибке."""
    try:
        response = requests.get(URL, params={'less_than_match_id': less_than_id}, timeout=30)
        if response.status_code == 200: 
            return response.json()
        else:
            logging.error(f"Error occurred while fetching data: {response.status_code}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error occurred while fetching data: {e}")
        return None
    
def save_batch(matches):
    """Сохраняет матчи в файл, добавляя каждому поле collected_at."""
    if not matches:
        logging.info("No matches to save.")
        return 
    with open(PATH, 'a', encoding='utf-8') as f:
        time_collected = int(time.time())
        for match in matches:
            match['collected_at'] = time_collected
            f.write(json.dumps(match) + '\n')
    logging.info(f"Saved {len(matches)} matches to {PATH}")

def get_newest_match_id():
    """Делает один запрос без параметров и возвращает match_id самого нового матча."""
    batch = fetch_batch(None)
    if not batch:
        logging.error('Failed to fetch the newest match id.')
        return None
    return max(match['match_id'] for match in batch)
    

def main():
    """Главная логика, определить старт, цикл по пачкам, счетчики, логи."""
    batches_done = 0  
    errors = 0
    max_batches = 250
    error_threshold = 5 
    last_id = get_newest_match_id()
    if last_id is None:
        logging.error('Could not determine the newest match id, exiting.')
        return
    while batches_done < max_batches:
        matches = fetch_batch(last_id)
        if matches is None:
            errors += 1
            logging.error(f"Error fetching batch. Total errors:{errors}")
            time.sleep(5)  # Sleep for a bit before retrying
            if errors >= error_threshold:
                logging.error("Error threshold reached. Stopping.")
                break
        elif not matches:
            logging.info("No more matches to fetch. Stopping.")
            break       
        else:
            save_batch(matches)
            last_id = min(match['match_id'] for match in matches)
            batches_done += 1
            logging.info(f"Batch {batches_done}/{max_batches}, last_id={last_id}")
            errors = 0   
            time.sleep(1)  # Sleep for a second to avoid hitting the API too quickly   


if __name__ == "__main__":
    main()