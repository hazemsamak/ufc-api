import requests
import pandas as pd
import re
import json
import hashlib
from datetime import datetime
import pytz
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag

COOKIES: Dict[str, str] = {}

def fetch_url(url: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
    """
    Fetch a URL using requests.get.
    Automatically solves UFCStats Cloudflare JavaScript POW challenge if present.
    """
    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    if headers:
        req_headers.update(headers)
        
    try:
        response = requests.get(url, headers=req_headers, cookies=COOKIES, timeout=10)
        
        # Check if UFCStats JS POW challenge is present
        if hasattr(response, 'text') and "ufcstats.com" in url and "b-statistics__table" not in response.text and "<title>Loading…" in response.text:
            nonce_match = re.search(r'nonce="([^"]+)"', response.text)
            target_match = re.search(r'target=new Array\((\d+)\+1\)', response.text)
            if nonce_match and target_match:
                nonce = nonce_match.group(1)
                target_len = int(target_match.group(1))
                target_str = '0' * target_len
                n = 0
                while True:
                    h = hashlib.sha256(f"{nonce}:{n}".encode('utf-8')).hexdigest()
                    if h.startswith(target_str):
                        break
                    n += 1
                post_resp = requests.post("http://ufcstats.com/__c", data={'nonce': nonce, 'n': str(n)}, headers=req_headers, timeout=10)
                if hasattr(post_resp, 'cookies'):
                    COOKIES.update(post_resp.cookies.get_dict())
                response = requests.get(url, headers=req_headers, cookies=COOKIES, timeout=10)
                
        return response
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        r = requests.Response()
        r.status_code = 500
        r._content = b""
        return r

def get_event_date_from_detail_page(event_url: str) -> str:
    """
    Get the actual event date from the event detail page
    """
    try:
        response = fetch_url(event_url)
        if response.status_code != 200:
            return "Date TBA"
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for date information in various possible locations
        date_info = soup.find('li', class_='b-list__box-list-item')
        if date_info and 'Date:' in date_info.get_text():
            date_text = str(date_info.get_text().replace('Date:', '').strip())
            return date_text
        
        # Alternative: look for date in event details
        details = soup.find_all('li', class_='b-list__box-list-item')
        for detail in details:
            text = detail.get_text()
            if 'Date:' in text:
                return str(text.replace('Date:', '').strip())
        
        return "Date TBA"
    except Exception:
        return "Date TBA"

def clean_event_name(event_name: str) -> str:
    """
    Clean event name to show only "UFC <number>" for numbered events
    For example: "UFC 325: Holloway vs. Oliveira" -> "UFC 325"
    Keep full name for other events like "UFC Fight Night: ..."
    """
    match = re.match(r'^(UFC\s+\d+)', event_name)
    if match:
        return match.group(1)
    return event_name

def get_upcoming_ufc_schedule() -> List[Dict[str, Any]]:
    """
    Scrape the upcoming UFC schedule from UFCStats.com (with fallback to Wikipedia)
    and return as list of dictionaries.
    """
    events_url = "http://ufcstats.com/statistics/events/upcoming"
    upcoming_events: List[Dict[str, Any]] = []

    # Fetch event mapping from Wikipedia for Fight Night numbers and names
    wiki_mapping = get_event_mapping_from_wikipedia()

    # Fetch ESPN timing info
    espn_schedule = get_espn_event_times()

    try:
        response = fetch_url(events_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the events table
            events_table = soup.find('table', class_='b-statistics__table-events')
            if not events_table:
                events_table = soup.find('table', class_='b-statistics__table')
            
            if events_table:
                tbody = events_table.find('tbody')
                if isinstance(tbody, Tag):
                    event_rows = tbody.find_all('tr')
                    for row in event_rows:
                        cols = row.find_all('td')
                        if len(cols) < 2:
                            continue
                            
                        # Extract event name and link from first column
                        event_link_tag = cols[0].find('a')
                        if not event_link_tag:
                            continue
                            
                        raw_event_name = event_link_tag.get_text(strip=True)
                        event_link = str(event_link_tag['href'])
                        
                        # Date directly from table span if available
                        date_span = cols[0].find('span')
                        if date_span and date_span.get_text(strip=True):
                            event_date = date_span.get_text(strip=True)
                        else:
                            event_date = get_event_date_from_detail_page(event_link)
                        
                        # Determine event type and number
                        event_type = "UFC"
                        event_number = None
                        
                        ufc_match = re.search(r'\bUFC\s+(\d+)\b', raw_event_name)
                        fn_match = re.search(r'\bFight Night\s+(\d+)\b', raw_event_name)
                        
                        if ufc_match:
                            event_type = "UFC"
                            event_number = ufc_match.group(1)
                        elif fn_match:
                            event_type = "UFC Fight Night"
                            event_number = fn_match.group(1)
                        elif "Fight Night" in raw_event_name:
                            event_type = "UFC Fight Night"
                            
                        if event_date in wiki_mapping:
                            wiki_name = wiki_mapping[event_date]
                            wiki_ufc_match = re.search(r'\bUFC\s+(\d+)\b', wiki_name)
                            wiki_fn_match = re.search(r'\bFight Night\s+(\d+)\b', wiki_name)
                            
                            if not event_number:
                                if wiki_ufc_match:
                                    event_number = wiki_ufc_match.group(1)
                                elif wiki_fn_match:
                                    event_number = wiki_fn_match.group(1)
                                    
                            if event_number and "Fight Night" in raw_event_name and not re.search(r'Fight Night\s+\d+', raw_event_name):
                                raw_event_name = re.sub(r'UFC Fight Night', f'UFC Fight Night {event_number}', raw_event_name, count=1)
                            elif ":" not in raw_event_name or raw_event_name.strip() == "UFC Fight Night":
                                raw_event_name = wiki_name

                        location = cols[1].get_text(strip=True)
                        
                        # Format date with ESPN time if available
                        final_event_date = event_date
                        try:
                            dt_ufc = pd.to_datetime(event_date)
                            date_key = dt_ufc.strftime('%Y-%m-%d')
                            if date_key in espn_schedule:
                                raw_time_str = espn_schedule[date_key]['time']
                                if "T" in raw_time_str:
                                    dt_utc = datetime.fromisoformat(raw_time_str.replace('Z', '+00:00'))
                                    gmt4 = pytz.timezone('Etc/GMT-4')
                                    dt_gmt4 = dt_utc.astimezone(gmt4)
                                    final_event_date = dt_gmt4.strftime('%B %d, %Y %I:%M %p')
                        except Exception:
                            pass

                        upcoming_events.append({
                            'event_date': final_event_date,
                            'event_type': event_type,
                            'event_name': raw_event_name,
                            'event_number': event_number,
                            'location': location
                        })
    except Exception as e:
        print(f"Error scraping UFCStats: {e}")

    # Fallback to Wikipedia if UFCStats yielded no events
    if not upcoming_events:
        upcoming_events = get_upcoming_events_from_wikipedia()
        # Enrich Wikipedia fallback with ESPN schedule times if available
        for event in upcoming_events:
            try:
                dt_ufc = pd.to_datetime(event['event_date'])
                date_key = dt_ufc.strftime('%Y-%m-%d')
                if date_key in espn_schedule:
                    raw_time_str = espn_schedule[date_key]['time']
                    if "T" in raw_time_str:
                        dt_utc = datetime.fromisoformat(raw_time_str.replace('Z', '+00:00'))
                        gmt4 = pytz.timezone('Etc/GMT-4')
                        dt_gmt4 = dt_utc.astimezone(gmt4)
                        event['event_date'] = dt_gmt4.strftime('%B %d, %Y %I:%M %p')
            except Exception:
                pass

    return upcoming_events

def get_upcoming_events_from_wikipedia() -> List[Dict[str, Any]]:
    """
    Scrape upcoming events directly from Wikipedia's scheduled events table as a fallback.
    Extracts and extrapolates all event numbers.
    """
    url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = fetch_url(url, headers=headers)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='wikitable')
        if not tables:
            return []
            
        target_table = None
        for table in tables:
            headers_list = [th.get_text(strip=True) for th in table.find_all('th')]
            if "Event" in headers_list and "Date" in headers_list:
                target_table = table
                break
                
        if not target_table:
            return []
            
        events = []
        rows = target_table.find_all('tr')
        raw_events: List[Dict[str, Any]] = []
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 3:
                raw_event_name = re.sub(r'\[.*?\]', '', cols[0].get_text(strip=True)).strip()
                raw_date = re.sub(r'\[.*?\]', '', cols[1].get_text(strip=True)).strip()
                venue = re.sub(r'\[.*?\]', '', cols[2].get_text(strip=True)).strip()
                location = re.sub(r'\[.*?\]', '', cols[3].get_text(strip=True)).strip() if len(cols) >= 4 else ''
                
                full_loc = f"{venue}, {location}" if venue and location else (venue or location)
                
                link = cols[0].find('a')
                href = link.get('href') if link else ''
                if isinstance(href, str) and not href.startswith("http"):
                    href = f"https://en.wikipedia.org{href}"
                    
                raw_events.append({
                    'raw_name': raw_event_name,
                    'raw_date': raw_date,
                    'location': full_loc,
                    'href': str(href)
                })

        # Extrapolate missing Fight Night numbers chronologically (earliest first)
        events_chrono = list(reversed(raw_events))
        for item in events_chrono:
            ename = item['raw_name']
            href = item['href']
            num = None
            
            m1 = re.search(r'\bUFC\s+(\d+)\b', ename)
            m2 = re.search(r'\bFight Night\s+(\d+)\b', ename)
            m3 = re.search(r'Fight_Night_(\d+)', href)
            m4 = re.search(r'UFC_(\d+)', href)
            
            if m1:
                num = m1.group(1)
            elif m2:
                num = m2.group(1)
            elif m3:
                num = m3.group(1)
            elif m4:
                num = m4.group(1)
                
            item['number'] = num

        fn_events = [e for e in events_chrono if "Fight Night" in e['raw_name']]
        for i in range(len(fn_events) - 1, -1, -1):
            if fn_events[i]['number'] is not None:
                try:
                    curr_num = int(fn_events[i]['number'])
                    for j in range(i - 1, -1, -1):
                        if fn_events[j]['number'] is None:
                            curr_num -= 1
                            fn_events[j]['number'] = str(curr_num)
                        else:
                            break
                except Exception:
                    pass

        for item in raw_events:
            raw_event_name = item['raw_name']
            raw_date = item['raw_date']
            full_loc = item['location']
            event_number = item['number']
            
            try:
                dt = pd.to_datetime(raw_date)
                event_date = dt.strftime('%B %d, %Y')
            except Exception:
                event_date = raw_date
                
            event_type = "UFC" if "UFC" in raw_event_name and "Fight Night" not in raw_event_name else "UFC Fight Night"
            
            if event_number and "Fight Night" in raw_event_name and not re.search(r'Fight Night\s+\d+', raw_event_name):
                raw_event_name = re.sub(r'UFC Fight Night', f'UFC Fight Night {event_number}', raw_event_name, count=1)
            elif event_number and "UFC" in raw_event_name and not re.search(r'UFC\s+\d+', raw_event_name):
                raw_event_name = re.sub(r'UFC', f'UFC {event_number}', raw_event_name, count=1)
                
            events.append({
                'event_date': event_date,
                'event_type': event_type,
                'event_name': raw_event_name,
                'event_number': event_number,
                'location': full_loc
            })
            
        return events
    except Exception as e:
        print(f"Error scraping Wikipedia fallback: {e}")
        return []

def get_espn_event_times() -> Dict[str, Dict[str, Any]]:
    """
    Scrape ESPN MMA schedule to get event start times.
    Returns a mapping of Date String (YYYY-MM-DD) -> {time, name}
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    schedule_data: Dict[str, Dict[str, Any]] = {}

    # 1. Try ESPN MMA scoreboard API first
    try:
        api_url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
        resp = requests.get(api_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            for event in data.get('events', []):
                name = event.get('name', '')
                date_iso = event.get('date', '')
                if date_iso:
                    dt = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
                    clean_date = dt.strftime('%Y-%m-%d')
                    schedule_data[clean_date] = {'time': date_iso, 'name': name}
    except Exception as e:
        print(f"Error fetching ESPN API: {e}")

    # 2. Try ESPN schedule HTML page for current year
    try:
        current_year = datetime.now().year
        url = f"https://www.espn.com/mma/schedule/_/year/{current_year}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200 and response.text:
            time_matches = re.findall(r'"date":"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)"', response.text)
            for tm in time_matches:
                dt = datetime.fromisoformat(tm.replace('Z', '+00:00'))
                clean_date = dt.strftime('%Y-%m-%d')
                if clean_date not in schedule_data:
                    schedule_data[clean_date] = {'time': tm, 'name': 'Unknown'}
    except Exception as e:
        print(f"Error fetching ESPN schedule HTML: {e}")

    return schedule_data

def get_event_mapping_from_wikipedia() -> Dict[str, str]:
    """
    Scrape upcoming events from Wikipedia to get the Fight Night numbers and event names.
    Returns a dictionary mapping Date -> Event Name (e.g. "February 10, 2024" -> "UFC Fight Night 236: Hermansson vs. Pyfer")
    """
    url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = fetch_url(url, headers=headers)
        if response.status_code != 200:
            return {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='wikitable')
        if not tables:
            return {}
        
        target_table = None
        for table in tables:
            headers_list = [th.get_text(strip=True) for th in table.find_all('th')]
            if "Event" in headers_list and "Date" in headers_list:
                target_table = table
                break
        
        mapping: Dict[str, str] = {}
        if target_table:
            rows = target_table.find_all('tr')
            raw_events: List[Dict[str, Any]] = []
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    event_col = cols[0]
                    date_col = cols[1]
                    
                    event_name = event_col.get_text(strip=True)
                    date_text = date_col.get_text(strip=True)
                    
                    event_name = re.sub(r'\[.*?\]', '', event_name).strip()
                    date_text = re.sub(r'\[.*?\]', '', date_text).strip()
                    
                    link = event_col.find('a')
                    href = link.get('href') if link else ''
                    if isinstance(href, str) and not href.startswith("http"):
                        href = f"https://en.wikipedia.org{href}"
                    
                    raw_events.append({
                        'event_name': event_name,
                        'date_text': date_text,
                        'href': str(href)
                    })

            # Extrapolate missing Fight Night numbers in chronological order
            events_chrono = list(reversed(raw_events))
            for item in events_chrono:
                ename = item['event_name']
                href = item['href']
                num = None
                
                m1 = re.search(r'\bUFC\s+(\d+)\b', ename)
                m2 = re.search(r'\bFight Night\s+(\d+)\b', ename)
                m3 = re.search(r'Fight_Night_(\d+)', href)
                m4 = re.search(r'UFC_(\d+)', href)
                
                if m1:
                    num = m1.group(1)
                elif m2:
                    num = m2.group(1)
                elif m3:
                    num = m3.group(1)
                elif m4:
                    num = m4.group(1)
                elif "Fight Night" in ename and href:
                    num = get_fight_night_number_from_wiki_url(href)
                    
                item['number'] = num

            fn_events = [e for e in events_chrono if "Fight Night" in e['event_name']]
            for i in range(len(fn_events) - 1, -1, -1):
                if fn_events[i]['number'] is not None:
                    try:
                        curr_num = int(fn_events[i]['number'])
                        for j in range(i - 1, -1, -1):
                            if fn_events[j]['number'] is None:
                                curr_num -= 1
                                fn_events[j]['number'] = str(curr_num)
                            else:
                                break
                    except Exception:
                        pass

            for item in raw_events:
                ename = item['event_name']
                num = item['number']
                date_text = item['date_text']
                
                if num and "Fight Night" in ename and not re.search(r'Fight Night\s+\d+', ename):
                    ename = re.sub(r'UFC Fight Night', f'UFC Fight Night {num}', ename, count=1)
                elif num and "UFC" in ename and not re.search(r'UFC\s+\d+', ename):
                    ename = re.sub(r'UFC', f'UFC {num}', ename, count=1)
                    
                mapping[date_text] = ename
                
                try:
                    dt = pd.to_datetime(date_text)
                    formatted_date_long = dt.strftime('%B %d, %Y')
                    mapping[formatted_date_long] = ename
                    
                    parts = formatted_date_long.split(' ')
                    if parts[1].startswith('0'):
                        parts[1] = parts[1][1:]
                    formatted_date_ufc_style = " ".join(parts)
                    mapping[formatted_date_ufc_style] = ename
                except Exception:
                    pass

        return mapping
    except Exception as e:
        print(f"Error scraping Wikipedia mapping: {e}")
        return {}

def get_fight_night_number_from_wiki_url(url: str) -> Optional[str]:
    """
    Fetch a Wikipedia event page and look for "UFC Fight Night <number>" in the text.
    Returns the number string (e.g. "267") or None.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = fetch_url(url, headers=headers)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        heading = soup.find('h1', id='firstHeading')
        if heading:
            match = re.search(r'UFC Fight Night\s+(\d+)', heading.get_text())
            if match:
                return match.group(1)
                
        paragraphs = soup.find_all('p')
        for p in paragraphs[:5]:
            match = re.search(r'UFC Fight Night\s+(\d+)', p.get_text())
            if match:
                return match.group(1)
                    
        return None
    except Exception:
        return None
