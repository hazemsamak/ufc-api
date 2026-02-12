import pytest
from bs4 import BeautifulSoup
import sys
import os

# Add src to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from scrapers.ufc_scraper import clean_event_name, get_event_date_from_detail_page, get_fight_night_number_from_wiki_url

def test_clean_event_name():
    """Test cleaning of event names"""
    assert clean_event_name("UFC 325: Holloway vs. Oliveira") == "UFC 325"
    assert clean_event_name("UFC Fight Night: Bautista vs. Oliveira") == "UFC Fight Night: Bautista vs. Oliveira"
    assert clean_event_name("UFC 300") == "UFC 300"
    assert clean_event_name("Fight Night") == "Fight Night"

def test_get_event_date_from_detail_page(mocker):
    """Test date extraction from event detail page with mocked requests"""
    mock_html = """
    <html>
        <body>
            <li class="b-list__box-list-item">
                <i class="b-list__box-item-title">Date:</i>
                February 08, 2025
            </li>
        </body>
    </html>
    """
    mock_response = mocker.Mock()
    mock_response.text = mock_html
    mock_response.status_code = 200
    mocker.patch('requests.get', return_value=mock_response)
    
    date = get_event_date_from_detail_page("http://example.com/event")
    assert date == "February 08, 2025"

def test_get_fight_night_number_from_wiki_url(mocker):
    """Test fight night number extraction from Wikipedia with mocked requests"""
    mock_html = """
    <html>
        <body>
            <p>UFC Fight Night 267: Some Content</p>
        </body>
    </html>
    """
    mock_response = mocker.Mock()
    mock_response.text = mock_html
    mock_response.status_code = 200
    mocker.patch('requests.get', return_value=mock_response)
    
    number = get_fight_night_number_from_wiki_url("http://example.com/wiki/Event")
    assert number == "267"

def test_get_fight_night_number_not_found(mocker):
    """Test when fight night number is not found"""
    mock_html = "<html><body>No number here</body></html>"
    mock_response = mocker.Mock()
    mock_response.text = mock_html
    mock_response.status_code = 200
    mocker.patch('requests.get', return_value=mock_response)
    
    number = get_fight_night_number_from_wiki_url("http://example.com/wiki/Event")
    assert number is None

def test_get_event_mapping_from_wikipedia(mocker):
    """Test Wikipedia event mapping with mocked requests"""
    mock_html = """
    <html>
        <body>
            <table class="wikitable">
                <tr><th>Event</th><th>Date</th></tr>
                <tr>
                    <td><a href="/wiki/UFC_Fight_Night_236">UFC Fight Night: Hermansson vs. Pyfer</a></td>
                    <td>February 10, 2024</td>
                </tr>
            </table>
        </body>
    </html>
    """
    mock_response = mocker.Mock()
    mock_response.text = mock_html
    mock_response.status_code = 200
    mocker.patch('requests.get', return_value=mock_response)
    # Mock get_fight_night_number_from_wiki_url to avoid sub-request
    mocker.patch('scrapers.ufc_scraper.get_fight_night_number_from_wiki_url', return_value="236")
    
    from scrapers.ufc_scraper import get_event_mapping_from_wikipedia
    mapping = get_event_mapping_from_wikipedia()
    
    assert "February 10, 2024" in mapping
    assert mapping["February 10, 2024"] == "UFC Fight Night 236"

def test_get_upcoming_ufc_schedule(mocker):
    """Test the full scraper orchestration with everything mocked"""
    mock_stats_html = """
    <table class="b-statistics__table-events">
        <tbody>
            <tr>
                <td><a href="http://ufcstats.com/event-details/123">UFC 325: Event</a></td>
                <td>Las Vegas, Nevada, USA</td>
            </tr>
        </tbody>
    </table>
    """
    
    # Mock requests for UFCStats
    mock_response = mocker.Mock()
    mock_response.text = mock_stats_html
    mock_response.status_code = 200
    mocker.patch('requests.get', return_value=mock_response)
    
    # Mock helpers
    mocker.patch('scrapers.ufc_scraper.get_event_mapping_from_wikipedia', return_value={})
    mocker.patch('scrapers.ufc_scraper.get_event_date_from_detail_page', return_value="February 21, 2026")
    
    from scrapers.ufc_scraper import get_upcoming_ufc_schedule
    events = get_upcoming_ufc_schedule()
    
    assert len(events) == 1
    assert events[0]['event_name'] == "UFC 325: Event"
    assert events[0]['event_type'] == "UFC"
    assert events[0]['event_number'] == "325"
    assert events[0]['location'] == "Las Vegas, Nevada, USA"
