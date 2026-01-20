from typing import List, Dict
from .notion_service import NotionClient

class HabitService:
    """
    Handles all habit-related operations.
    """

    def __init__(self):
        self.notion = NotionClient()

    def get_todays_habits(self) -> List[Dict]:
        """
        Fetch all active habits from Notion.
        
        Returns:
            List of habit objects.
        """
        return self.notion.fetch_active_habits()
