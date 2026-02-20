import requests
import pandas as pd
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag

def get_event_date_from_detail_page(event_url: str) -> str:
    """
    Get the actual event date from the event detail page
    """
    try:
        response = requests.get(event_url)
        response.raise_for_status()
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
    except:
        return "Date TBA"

def clean_event_name(event_name: str) -> str:
    """
    Clean event name to show only "UFC <number>" for numbered events
    For example: "UFC 325: Holloway vs. Oliveira" -> "UFC 325"
    Keep full name for other events like "UFC Fight Night: ..."
    """
    # Check if event starts with "UFC" followed by a space and a number
    match = re.match(r'^(UFC\s+\d+)', event_name)
    if match:
        # Return only "UFC <number>"
        return match.group(1)
    # Otherwise return the full event name (e.g., UFC Fight Night: ...)
    return event_name


def get_upcoming_ufc_schedule() -> List[Dict[str, Any]]:
    """
    Scrape the upcoming UFC schedule from UFCStats.com and return as list of dictionaries
    """
    events_url = "http://ufcstats.com/statistics/events/upcoming"
    
    response = requests.get(events_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the events table
    events_table = soup.find('table', class_='b-statistics__table-events')
    if not events_table:
        events_table = soup.find('table', class_='b-statistics__table')
        if not events_table:
            return []
    
    tbody = events_table.find('tbody')
    if not tbody:
        return []

    # Fetch event mapping from Wikipedia
    wiki_mapping = get_event_mapping_from_wikipedia()
    
    event_rows: List[Tag] = []
    if isinstance(tbody, Tag):
        event_rows = tbody.find_all('tr')
    else:
        return []
    
    upcoming_events = []
    
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
        
        # Determine event type and number
        event_type = "UFC"
        event_number = None
        
        # Check for "UFC <number>" pattern
        ufc_match = re.match(r'^UFC\s+(\d+)', raw_event_name)
        if ufc_match:
            event_type = "UFC"
            event_number = ufc_match.group(1)
        elif "Fight Night" in raw_event_name:
             event_type = "UFC Fight Night"
             # Try to find number in name first (unlikely for UFCStats but possible)
             fn_match = re.search(r'Fight Night\s+(\d+)', raw_event_name)
             if fn_match:
                 event_number = fn_match.group(1)
             else:
                 # Try Wikipedia mapping
                 # Get actual date from the event detail page
                 event_date = get_event_date_from_detail_page(event_link)
                 
                 # Check mapping
                 # The mapping keys are formatted dates.
                 # The values in mapping are "UFC Fight Night <number>" or similar.
                 
                 if event_date in wiki_mapping:
                     wiki_name = wiki_mapping[event_date]
                     # Extract number from wiki name
                     wiki_match = re.search(r'Fight Night\s+(\d+)', wiki_name)
                     if wiki_match:
                         event_number = wiki_match.group(1)
                         
                     # If the original name is just generic, use the Wikipedia name (which usually contains the fighters)
                     if ":" not in raw_event_name or raw_event_name.strip() == "UFC Fight Night":
                         raw_event_name = wiki_name

        # If we didn't get the date yet (numbered events Loop), get it now
        # Creating a local variable 'event_date' if not already set is risky in loop if branches differ.
        if 'event_date' not in locals():
             event_date = get_event_date_from_detail_page(event_link)

        # Extract location from second column
        location = cols[1].get_text(strip=True)
        
        upcoming_events.append({
            'event_date': event_date,
            'event_type': event_type,
            'event_name': raw_event_name,
            'event_number': event_number,
            'location': location
        })
        
        # Clean up local var for next iteration safety
        del event_date
    
    return upcoming_events

def get_event_mapping_from_wikipedia() -> Dict[str, str]:
    """
    Scrape upcoming events from Wikipedia to get the Fight Night numbers.
    Returns a dictionary mapping Date -> Event Name (e.g. "February 10, 2024" -> "UFC Fight Night 236")
    """
    url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
    try:
        response = requests.get(url)
        # Wikipedia might block requests without user agent
        if response.status_code != 200:
             response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find Scheduled events table
        # Strategy: Look for the headers "Event", "Date", "Venue"
        tables = soup.find_all('table', class_='wikitable')
        target_table = None
        for table in tables:
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            if "Event" in headers and "Date" in headers:
                target_table = table
                break
        
        mapping = {}
        if target_table:
            rows = target_table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    # Col 0: Event (link text)
                    # Col 1: Date
                    event_col = cols[0]
                    date_col = cols[1]
                    
                    event_name = event_col.get_text(strip=True)
                    date_text = date_col.get_text(strip=True)
                    
                    # Clean up footnote references [1], [a], etc. from event name
                    event_name = re.sub(r'\[.*?\]', '', event_name).strip()
                    
                    # Normalize date to match UFCStats format if possible?
                    # UFCStats: "February 10, 2024"
                    # Wikipedia: "Feb 10, 2024" or "February 10, 2024"
                    # We might need to be flexible or parse dates. 
                    # For now let's try to match exactly or basic transformation
                    # Let's clean the date text (remove [ref])
                    date_text = re.sub(r'\[.*?\]', '', date_text).strip()
                    
                    # If event name is just "UFC Fight Night: ..." without number, try to find it in the link
                    if "Fight Night" in event_name and not re.search(r'\d+', event_name):
                        link = event_col.find('a')
                        if link:
                            link_href = link.get('href')
                            if isinstance(link_href, str):
                                wiki_url = f"https://en.wikipedia.org{link_href}"
                                # Fetch detail page to find number
                                number = get_fight_night_number_from_wiki_url(wiki_url)
                                if number:
                                    # Construct new name e.g. "UFC Fight Night 250: Yan vs. Figueiredo"
                                    # Substitute number into event name while preserving the subtitle
                                    event_name = re.sub(r'UFC Fight Night', f'UFC Fight Night {number}', event_name, count=1)

                    mapping[date_text] = event_name
                    
                   
                        
                    try:
                        dt = pd.to_datetime(date_text)
                        
                        # "February 08, 2025"
                        formatted_date_long = dt.strftime('%B %d, %Y')
                        mapping[formatted_date_long] = event_name
                        
                        # Handle single digit day matching manually if needed or just strip 0
                        parts = formatted_date_long.split(' ')
                        if parts[1].startswith('0'):
                            parts[1] = parts[1][1:]
                        
                        formatted_date_ufc_style = " ".join(parts)
                        mapping[formatted_date_ufc_style] = event_name
                        
                    except:
                        pass
                        
        return mapping
    except Exception as e:
        print(f"Error scraping Wikipedia: {e}")
        return {}

def get_fight_night_number_from_wiki_url(url: str) -> Optional[str]:
    """
    Fetch a Wikipedia event page and look for "UFC Fight Night <number>" in the text.
    Returns the number string (e.g. "267") or None.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        # Look for pattern "UFC Fight Night <number>" in the main heading or first paragraphs
        # This avoids matching chronology infobox links to next/previous events.
        
        # 1. Check main heading
        heading = soup.find('h1', id='firstHeading')
        if heading:
            match = re.search(r'UFC Fight Night\s+(\d+)', heading.get_text())
            if match:
                return match.group(1)
                
        # 2. Check first paragraphs
        content = soup.find('div', class_='mw-parser-output')
        if content:
            for p in content.find_all('p', recursive=False)[:3]:
                match = re.search(r'UFC Fight Night\s+(\d+)', p.get_text())
                if match:
                    return match.group(1)
                    
        return None
    except:
        return None
