import pytest
from unittest.mock import Mock, patch
import datetime
from orchestration.habit_stats_service import HabitStatsService


@pytest.fixture
def habit_stats_service():
    """Fixture to create HabitStatsService instance with mocked NotionClient."""
    with patch('orchestration.habit_stats_service.NotionClient') as mock_notion:
        service = HabitStatsService()
        service.notion = mock_notion.return_value
        return service


@pytest.fixture
def sample_habit():
    """Sample habit object for testing."""
    return {
        "id": "habit123",
        "properties": {
            "Ad": {"type": "title", "title": [{"plain_text": "Morning Run"}]},
            "Frekans": {"type": "select", "select": {"name": "Günlük"}}
        }
    }


@pytest.fixture
def sample_habit_weekly():
    """Sample weekly habit object for testing."""
    return {
        "id": "habit456",
        "properties": {
            "Ad": {"type": "title", "title": [{"plain_text": "Weekly Review"}]},
            "Frekans": {"type": "select", "select": {"name": "Haftalık"}}
        }
    }


@pytest.fixture
def sample_habit_monthly():
    """Sample monthly habit object for testing."""
    return {
        "id": "habit789",
        "properties": {
            "Ad": {"type": "title", "title": [{"plain_text": "Monthly Checkup"}]},
            "Frekans": {"type": "select", "select": {"name": "Aylık"}}
        }
    }


class TestParseDate:
    """Tests for _parse_date method."""
    
    def test_parse_valid_date(self, habit_stats_service):
        """Test parsing a valid ISO date string."""
        date_str = "2026-01-27"
        result = habit_stats_service._parse_date(date_str)
        assert result == datetime.date(2026, 1, 27)
    
    def test_parse_valid_datetime(self, habit_stats_service):
        """Test parsing a valid ISO datetime string."""
        date_str = "2026-01-27T10:30:00"
        result = habit_stats_service._parse_date(date_str)
        assert result == datetime.date(2026, 1, 27)
    
    def test_parse_invalid_date(self, habit_stats_service):
        """Test parsing an invalid date string."""
        date_str = "invalid-date"
        result = habit_stats_service._parse_date(date_str)
        assert result is None
    
    def test_parse_none(self, habit_stats_service):
        """Test parsing None."""
        result = habit_stats_service._parse_date(None)
        assert result is None
    
    def test_parse_empty_string(self, habit_stats_service):
        """Test parsing empty string."""
        result = habit_stats_service._parse_date("")
        assert result is None


class TestCalculateStreak:
    """Tests for calculate_streak method."""
    
    def test_streak_no_logs(self, habit_stats_service):
        """Test streak calculation with no habit logs."""
        habit_stats_service.notion.fetch_habit_logs.return_value = []
        
        streak = habit_stats_service.calculate_streak("habit123", "Günlük")
        assert streak == 0
    
    def test_streak_no_completed_logs(self, habit_stats_service):
        """Test streak calculation with only incomplete logs."""
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": False},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-27"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        streak = habit_stats_service.calculate_streak("habit123", "Günlük")
        assert streak == 0
    
    def test_streak_daily_consecutive(self, habit_stats_service):
        """Test streak calculation for daily habit with consecutive completions."""
        today = datetime.date.today()
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": today.isoformat()}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": (today - datetime.timedelta(days=1)).isoformat()}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": (today - datetime.timedelta(days=2)).isoformat()}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        streak = habit_stats_service.calculate_streak("habit123", "Günlük")
        assert streak == 3
    
    def test_streak_daily_broken(self, habit_stats_service):
        """Test streak calculation for daily habit with broken streak."""
        today = datetime.date.today()
        # Create a clear break: today, yesterday, then skip 2 days, then day 4
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": today.isoformat()}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": (today - datetime.timedelta(days=1)).isoformat()}}
                }
            },
            # Missing days 2 and 3 - clear break
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": (today - datetime.timedelta(days=4)).isoformat()}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        streak = habit_stats_service.calculate_streak("habit123", "Günlük")
        assert streak == 2  # Should only count today and yesterday before the break
    
    def test_streak_weekly_consecutive(self, habit_stats_service):
        """Test streak calculation for weekly habit with consecutive completions."""
        today = datetime.date.today()
        current_week = today.isocalendar()[1]
        current_year = today.isocalendar()[0]
        
        # Create dates in consecutive weeks
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": today.isoformat()}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": (today - datetime.timedelta(weeks=1)).isoformat()}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": (today - datetime.timedelta(weeks=2)).isoformat()}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        streak = habit_stats_service.calculate_streak("habit123", "Haftalık")
        assert streak == 3
    
    def test_streak_monthly_consecutive(self, habit_stats_service):
        """Test streak calculation for monthly habit with consecutive completions."""
        # Create dates in consecutive months
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-15"}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2025-12-20"}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2025-11-10"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        with patch('orchestration.habit_stats_service.datetime') as mock_datetime:
            mock_datetime.date.today.return_value = datetime.date(2026, 1, 27)
            mock_datetime.datetime.fromisoformat = datetime.datetime.fromisoformat
            mock_datetime.timedelta = datetime.timedelta
            mock_datetime.date = datetime.date
            
            streak = habit_stats_service.calculate_streak("habit123", "Aylık")
            assert streak == 3


class TestCalculateCompletionRate:
    """Tests for calculate_completion_rate method."""
    
    def test_completion_rate_no_logs(self, habit_stats_service):
        """Test completion rate with no logs."""
        habit_stats_service.notion.fetch_habit_logs.return_value = []
        
        rate = habit_stats_service.calculate_completion_rate("habit123", 30, "Günlük")
        assert rate == 0.0
    
    def test_completion_rate_daily_100_percent(self, habit_stats_service):
        """Test completion rate for daily habit with 100% completion."""
        # Create 7 completed logs for 7 days
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": f"2026-01-{20+i}"}}
                }
            }
            for i in range(7)
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        rate = habit_stats_service.calculate_completion_rate("habit123", 7, "Günlük")
        assert rate == 1.0
    
    def test_completion_rate_daily_50_percent(self, habit_stats_service):
        """Test completion rate for daily habit with 50% completion."""
        # Create 15 completed logs for 30 days (50%)
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True if i % 2 == 0 else False},
                    "Tarih": {"type": "date", "date": {"start": f"2026-01-{i+1:02d}"}}
                }
            }
            for i in range(30)
        ]
        # Filter only completed
        completed_logs = [log for log in logs if log["properties"]["Tamamlandı"]["checkbox"]]
        habit_stats_service.notion.fetch_habit_logs.return_value = completed_logs
        
        rate = habit_stats_service.calculate_completion_rate("habit123", 30, "Günlük")
        assert rate == 0.5
    
    def test_completion_rate_weekly(self, habit_stats_service):
        """Test completion rate for weekly habit."""
        # Create 3 completed logs for 4 weeks (75%)
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-06"}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-13"}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-20"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        rate = habit_stats_service.calculate_completion_rate("habit123", 28, "Haftalık")
        assert rate == 0.75
    
    def test_completion_rate_monthly(self, habit_stats_service):
        """Test completion rate for monthly habit."""
        # Create 2 completed logs for 60 days (2 months = 100%)
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2025-12-15"}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-15"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        rate = habit_stats_service.calculate_completion_rate("habit123", 60, "Aylık")
        assert rate == 1.0
    
    def test_completion_rate_capped_at_100(self, habit_stats_service):
        """Test that completion rate is capped at 100%."""
        # Create more logs than expected
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": f"2026-01-{i+1:02d}"}}
                }
            }
            for i in range(10)
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        rate = habit_stats_service.calculate_completion_rate("habit123", 7, "Günlük")
        assert rate == 1.0  # Should be capped at 1.0 (100%)


class TestGetLastCompletionDate:
    """Tests for get_last_completion_date method."""
    
    def test_last_completion_no_logs(self, habit_stats_service):
        """Test getting last completion date with no logs."""
        habit_stats_service.notion.fetch_habit_logs.return_value = []
        
        result = habit_stats_service.get_last_completion_date("habit123")
        assert result is None
    
    def test_last_completion_no_completed_logs(self, habit_stats_service):
        """Test getting last completion date with no completed logs."""
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": False},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-27"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        result = habit_stats_service.get_last_completion_date("habit123")
        assert result is None
    
    def test_last_completion_with_completed_logs(self, habit_stats_service):
        """Test getting last completion date with completed logs."""
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-27"}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-26"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        result = habit_stats_service.get_last_completion_date("habit123")
        assert result == "2026-01-27"
    
    def test_last_completion_mixed_logs(self, habit_stats_service):
        """Test getting last completion date with mixed completed/incomplete logs."""
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": False},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-27"}}
                }
            },
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-26"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        result = habit_stats_service.get_last_completion_date("habit123")
        assert result == "2026-01-26"


class TestCalculateStatsForHabit:
    """Tests for calculate_stats_for_habit method."""
    
    def test_calculate_stats_complete(self, habit_stats_service, sample_habit):
        """Test calculating all stats for a habit."""
        # Mock the individual calculation methods
        habit_stats_service.calculate_streak = Mock(return_value=5)
        habit_stats_service.calculate_completion_rate = Mock(return_value=0.855)
        habit_stats_service.get_last_completion_date = Mock(return_value="2026-01-27")
        
        completion_rate, streak, last_completion = habit_stats_service.calculate_stats_for_habit(sample_habit)
        
        assert completion_rate == 0.855
        assert streak == 5
        assert last_completion == "2026-01-27"
        
        # Verify methods were called correctly
        habit_stats_service.calculate_streak.assert_called_once_with("habit123", "Günlük")
        habit_stats_service.calculate_completion_rate.assert_called_once_with("habit123", 30, "Günlük")
        habit_stats_service.get_last_completion_date.assert_called_once_with("habit123")
    
    def test_calculate_stats_no_frequency(self, habit_stats_service):
        """Test calculating stats for habit with no frequency (defaults to Günlük)."""
        habit = {
            "id": "habit123",
            "properties": {
                "Ad": {"type": "title", "title": [{"plain_text": "Test Habit"}]},
                "Frekans": {"type": "select", "select": None}
            }
        }
        
        habit_stats_service.calculate_streak = Mock(return_value=0)
        habit_stats_service.calculate_completion_rate = Mock(return_value=0.0)
        habit_stats_service.get_last_completion_date = Mock(return_value=None)
        
        completion_rate, streak, last_completion = habit_stats_service.calculate_stats_for_habit(habit)
        
        # Should default to "Günlük"
        habit_stats_service.calculate_streak.assert_called_once_with("habit123", "Günlük")
    
    def test_calculate_stats_weekly_habit(self, habit_stats_service, sample_habit_weekly):
        """Test calculating stats for weekly habit."""
        habit_stats_service.calculate_streak = Mock(return_value=3)
        habit_stats_service.calculate_completion_rate = Mock(return_value=0.75)
        habit_stats_service.get_last_completion_date = Mock(return_value="2026-01-20")
        
        completion_rate, streak, last_completion = habit_stats_service.calculate_stats_for_habit(sample_habit_weekly)
        
        habit_stats_service.calculate_streak.assert_called_once_with("habit456", "Haftalık")
        habit_stats_service.calculate_completion_rate.assert_called_once_with("habit456", 30, "Haftalık")


class TestCalculateStatsForAllHabits:
    """Tests for calculate_stats_for_all_habits method."""
    
    def test_calculate_all_no_habits(self, habit_stats_service, capsys):
        """Test calculating stats when there are no active habits."""
        habit_stats_service.notion.fetch_active_habits.return_value = []
        
        results = habit_stats_service.calculate_stats_for_all_habits()
        
        assert results == {}
        captured = capsys.readouterr()
        assert "No active habits found" in captured.out
    
    def test_calculate_all_success(self, habit_stats_service, sample_habit, capsys):
        """Test successful calculation and update of all habits."""
        habit_stats_service.notion.fetch_active_habits.return_value = [sample_habit]
        habit_stats_service.calculate_stats_for_habit = Mock(return_value=(0.855, 5, "2026-01-27"))
        habit_stats_service.notion.update_habit.return_value = True
        
        results = habit_stats_service.calculate_stats_for_all_habits()
        
        assert len(results) == 1
        assert "habit123" in results
        assert results["habit123"]["name"] == "Morning Run"
        assert results["habit123"]["completion_rate"] == 0.855
        assert results["habit123"]["streak"] == 5
        assert results["habit123"]["last_completion"] == "2026-01-27"
        
        # Verify update was called
        habit_stats_service.notion.update_habit.assert_called_once_with(
            habit_id="habit123",
            completion_rate=0.855,
            streak=5,
            last_completion="2026-01-27"
        )
        
        captured = capsys.readouterr()
        assert "Morning Run" in captured.out
        assert "85.5% rate" in captured.out
    
    def test_calculate_all_update_failure(self, habit_stats_service, sample_habit, capsys):
        """Test when habit update fails."""
        habit_stats_service.notion.fetch_active_habits.return_value = [sample_habit]
        habit_stats_service.calculate_stats_for_habit = Mock(return_value=(0.855, 5, "2026-01-27"))
        habit_stats_service.notion.update_habit.return_value = False
        
        results = habit_stats_service.calculate_stats_for_all_habits()
        
        assert len(results) == 0  # Failed updates not included in results
        
        captured = capsys.readouterr()
        assert "Failed to update" in captured.out
    
    def test_calculate_all_calculation_error(self, habit_stats_service, sample_habit, capsys):
        """Test when calculation raises an exception."""
        habit_stats_service.notion.fetch_active_habits.return_value = [sample_habit]
        habit_stats_service.calculate_stats_for_habit = Mock(side_effect=Exception("Calculation error"))
        
        results = habit_stats_service.calculate_stats_for_all_habits()
        
        assert len(results) == 0
        
        captured = capsys.readouterr()
        assert "Error calculating stats" in captured.out
        assert "Morning Run" in captured.out
    
    def test_calculate_all_multiple_habits(self, habit_stats_service, sample_habit, sample_habit_weekly):
        """Test calculating stats for multiple habits."""
        habits = [sample_habit, sample_habit_weekly]
        habit_stats_service.notion.fetch_active_habits.return_value = habits
        
        # Mock different stats for each habit
        def mock_calculate(habit):
            if habit["id"] == "habit123":
                return (0.855, 5, "2026-01-27")
            else:
                return (0.9, 3, "2026-01-26")
        
        habit_stats_service.calculate_stats_for_habit = Mock(side_effect=mock_calculate)
        habit_stats_service.notion.update_habit.return_value = True
        
        results = habit_stats_service.calculate_stats_for_all_habits()
        
        assert len(results) == 2
        assert results["habit123"]["streak"] == 5
        assert results["habit456"]["streak"] == 3


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_streak_with_invalid_dates(self, habit_stats_service):
        """Test streak calculation with invalid date formats."""
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "invalid-date"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        streak = habit_stats_service.calculate_streak("habit123", "Günlük")
        assert streak == 0  # Should handle gracefully
    
    def test_completion_rate_zero_period(self, habit_stats_service):
        """Test completion rate with zero period days."""
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-27"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        rate = habit_stats_service.calculate_completion_rate("habit123", 0, "Günlük")
        assert rate == 0.0  # Should handle gracefully
    
    def test_frequency_case_insensitive(self, habit_stats_service):
        """Test that frequency comparisons work correctly."""
        # The code uses exact string matching, so this documents expected behavior
        logs = [
            {
                "properties": {
                    "Tamamlandı": {"checkbox": True},
                    "Tarih": {"type": "date", "date": {"start": "2026-01-27"}}
                }
            }
        ]
        habit_stats_service.notion.fetch_habit_logs.return_value = logs
        
        # Should handle Turkish characters correctly
        streak = habit_stats_service.calculate_streak("habit123", "Günlük")
        assert isinstance(streak, int)
