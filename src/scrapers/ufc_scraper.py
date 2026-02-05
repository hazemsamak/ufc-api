import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_event_date_from_detail_page(event_url):
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
            date_text = date_info.get_text().replace('Date:', '').strip()
            return date_text
        
        # Alternative: look for date in event details
        details = soup.find_all('li', class_='b-list__box-list-item')
        for detail in details:
            text = detail.get_text()
            if 'Date:' in text:
                return text.replace('Date:', '').strip()
        
        return "Date TBA"
    except:
        return "Date TBA"

def clean_event_name(event_name):
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


def get_upcoming_ufc_schedule():
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
    
    event_rows = tbody.find_all('tr')
    upcoming_events = []
    
    for row in event_rows:
        cols = row.find_all('td')
        
        if len(cols) < 2:
            continue
            
        # Extract event name and link from first column
        event_link_tag = cols[0].find('a')
        if not event_link_tag:
            continue
            
        event_name = event_link_tag.get_text(strip=True)
        event_link = event_link_tag['href']
        
        # Clean event name (e.g., "UFC 325: Title" -> "UFC 325")
        event_name = clean_event_name(event_name)
        
        # Extract location from second column
        location = cols[1].get_text(strip=True)
        
        # Get actual date from the event detail page
        event_date = get_event_date_from_detail_page(event_link)
        
        upcoming_events.append({
            'event_name': event_name,
            'event_date': event_date,
            'location': location
        })
    
    return upcoming_events
