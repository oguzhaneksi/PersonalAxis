import pytest
import datetime
from unittest.mock import MagicMock, patch
from orchestration.context_generator import ContextGenerator

@pytest.fixture
def generator(mocker):
    # Mock NotionClient to avoid real API calls and focus on logic
    mocker.patch("orchestration.context_generator.NotionClient")
    return ContextGenerator()

def test_get_period_explicit(generator):
    """Test that explicit period is returned as is."""
    assert generator.get_period("weekly", "2026-W01") == "2026-W01"
    assert generator.get_period("monthly", "2026-01") == "2026-01"

def test_get_period_current_weekly(generator, mocker):
    """Test current week calculation."""
    # Mock datetime to a specific date
    fixed_now = datetime.datetime(2026, 1, 20) # Tuesday
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    generator.notion._calculate_week.return_value = "2026-W04"
    
    assert generator.get_period("weekly", None) == "2026-W04"
    generator.notion._calculate_week.assert_called_once_with("2026-01-20")

def test_get_period_last_weekly(generator, mocker):
    """Test 'last' week calculation."""
    # Jan 20th 2026 (Tuesday)
    fixed_now = datetime.datetime(2026, 1, 20)
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    generator.notion._calculate_week.return_value = "2026-W03"
    
    # In 'last' weekly, it should subtract 7 days -> Jan 13th
    result = generator.get_period("weekly", "last")
    
    assert result == "2026-W03"
    generator.notion._calculate_week.assert_called_once_with("2026-01-13")

def test_get_period_last_monthly(generator, mocker):
    """Test 'last' month calculation."""
    fixed_now = datetime.datetime(2026, 2, 1) # Feb 1st
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    generator.notion._calculate_month.return_value = "2026-01"
    
    # In 'last' monthly, it should go to Jan (previous month)
    result = generator.get_period("monthly", "last")
    
    assert result == "2026-01"
    # Logic in get_period for monthly 'last' uses replace(day=1) - delta(days=1)
    # Feb 1 -> Jan 31
    generator.notion._calculate_month.assert_called_once_with("2026-01-31")

def test_get_period_last_yearly(generator, mocker):
    """Test 'last' year calculation."""
    fixed_now = datetime.datetime(2026, 1, 20)
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    generator.notion._calculate_year.return_value = "2025"
    
    result = generator.get_period("yearly", "last")
    
    assert result == "2025"
    # 2026-01-20 - 1 year -> 2025-01-20
    generator.notion._calculate_year.assert_called_once_with("2025-01-20")

def test_get_period_last_quarterly(generator, mocker):
    """Test 'last' quarter calculation."""
    fixed_now = datetime.datetime(2026, 4, 15) # Q2
    mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    generator.notion._calculate_quarter.return_value = "2026-Q1"
    
    result = generator.get_period("quarterly", "last")
    
    assert result == "2026-Q1"
    # Q2 (April) - 3 months -> Jan
    generator.notion._calculate_quarter.assert_called_once_with("2026-01-15")
