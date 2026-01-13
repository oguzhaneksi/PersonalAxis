#!/usr/bin/env python3
"""
Quick verification script to test the new period calculation functions.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestration.notion_service import NotionClient

def test_period_calculations():
    """Test the period calculation helper functions."""
    client = NotionClient()
    
    test_dates = [
        "2026-01-13",  # Monday, Week 3, Q1
        "2026-03-31",  # Last day of Q1
        "2026-04-01",  # First day of Q2
        "2026-12-31",  # Last day of year
    ]
    
    print("Testing Period Calculation Functions\n" + "="*50)
    
    for date_str in test_dates:
        print(f"\nDate: {date_str}")
        print(f"  Hafta:   {client._calculate_week(date_str)}")
        print(f"  Ay:      {client._calculate_month(date_str)}")
        print(f"  Çeyrek:  {client._calculate_quarter(date_str)}")
        print(f"  Yıl:     {client._calculate_year(date_str)}")
    
    print("\n" + "="*50)
    print("✓ All calculations completed successfully!")

if __name__ == "__main__":
    test_period_calculations()
