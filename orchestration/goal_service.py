from typing import List, Dict, Optional
from .notion_service import NotionClient

class GoalService:
    """
    Handles all goal-related operations.
    """

    def __init__(self):
        self.notion = NotionClient()

    def get_active_goals(self, period_type: Optional[str] = None, period: Optional[str] = None) -> List[Dict]:
        """
        Fetch active periodic goals.
        
        Args:
            period_type: Type of period (Yıllık, Çeyreklik, Aylık, Haftalık)
            period: Period identifier (e.g., "2026", "2026-Q1")
            
        Returns:
            List of goal objects.
        """
        return self.notion.fetch_active_goals(period_type=period_type, period=period)
