import pytest
import datetime
from unittest.mock import MagicMock, patch
from orchestration.review_service import ReviewService

@pytest.fixture
def review_service(mocker):
    # Mock NotionClient to avoid real API calls and focus on logic
    mocker.patch("orchestration.review_service.NotionClient")
    return ReviewService()

def test_get_period_explicit(review_service):
    """Test that explicit period is returned as is."""
    assert review_service.calculate_period("weekly", "2026-W01") == "2026-W01"
    assert review_service.calculate_period("monthly", "2026-01") == "2026-01"

def test_get_period_current_weekly(review_service, mocker):
    """Test current week calculation."""
    # Mock datetime to a specific date
    fixed_now = datetime.datetime(2026, 1, 20) # Tuesday
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    review_service.notion._calculate_week.return_value = "2026-W04"
    
    assert review_service.calculate_period("weekly", None) == "2026-W04"
    review_service.notion._calculate_week.assert_called_once_with("2026-01-20")

def test_get_period_last_weekly(review_service, mocker):
    """Test 'last' week calculation."""
    # Jan 20th 2026 (Tuesday)
    fixed_now = datetime.datetime(2026, 1, 20)
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    review_service.notion._calculate_week.return_value = "2026-W03"
    
    # In 'last' weekly, it should subtract 7 days -> Jan 13th
    result = review_service.calculate_period("weekly", "last")
    
    assert result == "2026-W03"
    review_service.notion._calculate_week.assert_called_once_with("2026-01-13")

def test_get_period_last_monthly(review_service, mocker):
    """Test 'last' month calculation."""
    fixed_now = datetime.datetime(2026, 2, 1) # Feb 1st
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    review_service.notion._calculate_month.return_value = "2026-01"
    
    # In 'last' monthly, it should go to Jan (previous month)
    result = review_service.calculate_period("monthly", "last")
    
    assert result == "2026-01"
    # Logic in calculate_period for monthly 'last' uses replace(day=1) - delta(days=1)
    # Feb 1 -> Jan 31
    review_service.notion._calculate_month.assert_called_once_with("2026-01-31")

def test_get_period_last_yearly(review_service, mocker):
    """Test 'last' year calculation."""
    fixed_now = datetime.datetime(2026, 1, 20)
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    review_service.notion._calculate_year.return_value = "2025"
    
    result = review_service.calculate_period("yearly", "last")
    
    assert result == "2025"
    # 2026-01-20 - 1 year -> 2025-01-20
    review_service.notion._calculate_year.assert_called_once_with("2025-01-20")

def test_get_period_last_quarterly(review_service, mocker):
    """Test 'last' quarter calculation."""
    fixed_now = datetime.datetime(2026, 4, 15) # Q2
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    review_service.notion._calculate_quarter.return_value = "2026-Q1"
    
    result = review_service.calculate_period("quarterly", "last")
    
    assert result == "2026-Q1"
    # Q2 (April) - 3 months -> Jan
    review_service.notion._calculate_quarter.assert_called_once_with("2026-01-15")
