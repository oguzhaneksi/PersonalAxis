import os
import sys
import datetime
from typing import Any, Dict, List, Optional
from notion_client import Client
from notion_client.errors import APIResponseError
from dotenv import load_dotenv

load_dotenv()

class NotionClient:
    """
    A wrapper for Notion API operations specifically tailored for PersonalAxis.
    """

    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        if not self.token:
            raise ValueError("NOTION_TOKEN not found in environment")
        
        self.client = Client(auth=self.token)
        
        # Load Database IDs
        self.db_ids = {
            "pillars": os.getenv("PILLARS_DB_ID"),
            "lt_goals": os.getenv("LT_GOALS_DB_ID"),
            "habits": os.getenv("HABITS_DB_ID"),
            "habit_logs": os.getenv("HABIT_LOGS_DB_ID"),
            "periodic_goals": os.getenv("PERIODIC_GOALS_DB_ID"),
            "actions": os.getenv("ACTIONS_DB_ID"),
            "journal": os.getenv("JOURNAL_DB_ID"),
            "reviews": os.getenv("REVIEWS_DB_ID"),
        }
        
        # Validate that all required IDs are present
        missing_ids = [name for name, db_id in self.db_ids.items() if not db_id]
        if missing_ids:
            print(f"Warning: Missing database IDs for: {', '.join(missing_ids)}")

    def _safe_query(self, database_id: str, query_filter: Optional[Dict] = None) -> List[Dict]:
        """
        Safely query a Notion database with error handling.
        """
        if not database_id:
            print(f"Error: Database ID missing for query.")
            return []

        try:
            results = []
            has_more = True
            start_cursor = None
            
            while has_more:
                response = self.client.databases.query(
                    database_id=database_id,
                    filter=query_filter,
                    start_cursor=start_cursor
                )
                results.extend(response.get("results", []))
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")
                
            return results
        except APIResponseError as e:
            print(f"Notion API Error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error querying database: {e}")
            return []

    def fetch_page_content(self, page_id: str) -> str:
        """
        Fetch all blocks for a page and convert to a basic Markdown-like string.
        """
        try:
            blocks = []
            has_more = True
            start_cursor = None
            
            while has_more:
                response = self.client.blocks.children.list(
                    block_id=page_id,
                    start_cursor=start_cursor
                )
                blocks.extend(response.get("results", []))
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")
                
            return self._parse_blocks_to_markdown(blocks)
        except Exception as e:
            print(f"Error fetching page content for {page_id}: {e}")
            return ""

    def _parse_blocks_to_markdown(self, blocks: List[Dict]) -> str:
        """
        Convert Notion blocks to a simplified Markdown string.
        """
        md_lines = []
        for block in blocks:
            b_type = block.get("type")
            if not b_type:
                continue
                
            content = block.get(b_type, {})
            text_items = content.get("rich_text", [])
            plain_text = "".join([t.get("plain_text", "") for t in text_items])
            
            if not plain_text and b_type != "divider":
                continue
                
            if b_type == "paragraph":
                md_lines.append(plain_text)
            elif b_type == "heading_1":
                md_lines.append(f"# {plain_text}")
            elif b_type == "heading_2":
                md_lines.append(f"## {plain_text}")
            elif b_type == "heading_3":
                md_lines.append(f"### {plain_text}")
            elif b_type == "bulleted_list_item":
                md_lines.append(f"- {plain_text}")
            elif b_type == "numbered_list_item":
                md_lines.append(f"1. {plain_text}")
            elif b_type == "to_do":
                checked = "x" if content.get("checked") else " "
                md_lines.append(f"- [{checked}] {plain_text}")
            elif b_type == "quote":
                md_lines.append(f"> {plain_text}")
            elif b_type == "divider":
                md_lines.append("---")
            elif b_type == "callout":
                icon = content.get("icon", {}).get("emoji", "ℹ️")
                md_lines.append(f"> {icon} {plain_text}")
                
        return "\n\n".join(md_lines)

    def _calculate_week(self, date_str: str) -> str:
        """Calculate ISO week format (e.g., 2026-W02) from date string."""
        dt = datetime.datetime.fromisoformat(date_str)
        year, week, _ = dt.isocalendar()
        return f"{year}-W{week:02d}"

    def _calculate_month(self, date_str: str) -> str:
        """Calculate month format (e.g., 2026-01) from date string."""
        dt = datetime.datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m")

    def _calculate_quarter(self, date_str: str) -> str:
        """Calculate quarter format (e.g., 2026-Q3) from date string."""
        dt = datetime.datetime.fromisoformat(date_str)
        quarter = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{quarter}"

    def _calculate_year(self, date_str: str) -> str:
        """Calculate year format (e.g., 2026) from date string."""
        dt = datetime.datetime.fromisoformat(date_str)
        return str(dt.year)

    def fetch_all_pillars(self) -> List[Dict]:
        """
        Fetch all active pillars from Notion.
        
        Returns:
            List of pillar objects.
        """
        pillar_filter = {
            "property": "Durum",
            "select": {
                "equals": "Aktif"
            }
        }
        return self._safe_query(self.db_ids["pillars"], pillar_filter)

    def fetch_active_goals(self, period_type: Optional[str] = None, period: Optional[str] = None) -> List[Dict]:
        """
        Fetch active periodic goals.
        
        Args:
            period_type: Type of period (Yıllık, Çeyreklik, Aylık, Haftalık)
            period: Period identifier (e.g., "2026", "2026-Q1")
            
        Returns:
            List of goal objects.
        """
        filters = []
        
        # Always filter for non-completed/non-deferred goals unless specific ones requested?
        # For context building, we usually want "Devam Ediyor" or "Başlanmadı"
        filters.append({
            "property": "Durum",
            "select": {
                "does_not_equal": "Ertelendi"
            }
        })
        filters.append({
            "property": "Durum",
            "select": {
                "does_not_equal": "Tamamlandı"
            }
        })
        
        if period_type:
            filters.append({
                "property": "Dönem Tipi",
                "select": {
                    "equals": period_type
                }
            })
            
        if period:
            filters.append({
                "property": "Dönem",
                "rich_text": {
                    "equals": period
                }
            })
            
        query_filter = {"and": filters} if len(filters) > 1 else filters[0]
        return self._safe_query(self.db_ids["periodic_goals"], query_filter)

    def fetch_active_habits(self) -> List[Dict]:
        """
        Fetch all active habits.
        
        Returns:
            List of habit objects.
        """
        habit_filter = {
            "property": "Durum",
            "select": {
                "equals": "Aktif"
            }
        }
        return self._safe_query(self.db_ids["habits"], habit_filter)

    def fetch_recent_journals(self, days: int = 7) -> List[Dict]:
        """
        Fetch journal entries from the last X days.
        """
        # Note: We need a Date filter. The 'Tarih' property is the Date objects.
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        journal_filter = {
            "property": "Tarih",
            "date": {
                "on_or_after": cutoff_date
            }
        }
        
        # Sort by date descending
        try:
            response = self.client.databases.query(
                database_id=self.db_ids["journal"],
                filter=journal_filter,
                sorts=[{"property": "Tarih", "direction": "descending"}]
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Error fetching recent journals: {e}")
            return []

    def fetch_journals_by_period(self, period_field: str, period_value: str) -> List[Dict]:
        """
        Fetch journals filtered by period (Hafta, Ay, Çeyrek, Yıl).
        
        Args:
            period_field: "Hafta", "Ay", "Çeyrek", or "Yıl"
            period_value: e.g., "2026-W02", "2026-01", "2026-Q1", "2026"
            
        Returns:
            List of journal objects matching the period.
        """
        journal_filter = {
            "property": period_field,
            "formula": {
                "string": {
                    "equals": period_value
                }
            }
        }
        
        try:
            response = self.client.databases.query(
                database_id=self.db_ids["journal"],
                filter=journal_filter,
                sorts=[{"property": "Tarih", "direction": "descending"}]
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Error fetching journals by {period_field}={period_value}: {e}")
            return []

    def fetch_tasks(self, date: Optional[str] = None) -> List[Dict]:
        """
        Fetch tasks for a specific day.
        
        Args:
            date: ISO date string (YYYY-MM-DD). Defaults to today.
        """
        if not date:
            import datetime
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            
        task_filter = {
            "and": [
                {
                    "property": "Yapma Tarihi",
                    "date": {
                        "on_or_before": date
                    }
                },
                {
                    "property": "Durum",
                    "select": {
                        "equals": "Aktif"
                    }
                }
            ]
        }
        return self._safe_query(self.db_ids["actions"], task_filter)

    def create_journal_entry(self, date_str: str, title: str, content: str, emotions: List[str] = None, insights: str = None) -> str:
        """
        Create a new journal entry in Notion.
        
        Args:
            date_str: ISO date string (YYYY-MM-DD)
            title: Title for the entry (usually the date code)
            content: Raw conversation content
            emotions: List of detected emotions
            insights: Extracted insights
            
        Returns:
            ID of the created page.
        """
        if not self.db_ids["journal"]:
            return "Error: Journal DB ID missing"

        properties = {
            "Tarih Kodu": {"title": [{"text": {"content": title}}]},
            "Tarih": {"date": {"start": date_str}},
        }
        
        # We could add emotions as multi-select if the property existed
        # For now, we'll put everything in the page content
        
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": "Giriş"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": content[:2000]}}]} # Notion limit per block
            }
        ]
        
        if emotions:
            children.extend([
                {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Duygular"}}]}},
                {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": ", ".join(emotions)}}]}}
            ])
            
        if insights:
            children.extend([
                {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Önemli İçgörüler"}}]}},
                {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": insights}}]}}
            ])

        try:
            response = self.client.pages.create(
                parent={"database_id": self.db_ids["journal"]},
                properties=properties,
                children=children
            )
            return response["id"]
        except Exception as e:
            print(f"Error creating journal entry: {e}")
            return ""

    def create_task(self, name: str, priority: str = "P3", date: str = None, status: str = "Aktif", pillar_id: str = None) -> str:
        """
        Create a new task in actions database.
        """
        if not self.db_ids["actions"]:
            return ""
            
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")

        properties = {
            "Ad": {"title": [{"text": {"content": name}}]},
            "Öncelik": {"select": {"name": priority}},
            "Yapma Tarihi": {"date": {"start": date}},
            "Durum": {"select": {"name": status}}
        }
        
        if pillar_id:
            properties["Sütun"] = {"relation": [{"id": pillar_id}]}

        try:
            response = self.client.pages.create(
                parent={"database_id": self.db_ids["actions"]},
                properties=properties
            )
            return response["id"]
        except Exception as e:
            print(f"Error creating task: {e}")
            return ""

    def create_review_session(self, review_type: str, period: str, summary: str, assessment: str, wins: List[str] = None, challenges: List[str] = None, lessons_learned: str = None, next_period_focus: List[str] = None) -> str:
        """
        Create a new review session entry in Notion.
        """
        if not self.db_ids["reviews"]:
            return ""

        # Map review_type to Turkish schema options
        type_mapping = {
            "weekly": "Haftalık",
            "monthly": "Aylık",
            "quarterly": "Çeyreklik",
            "yearly": "Yıllık"
        }
        mapped_type = type_mapping.get(review_type.lower(), "Haftalık")

        properties = {
            "Dönem": {"title": [{"text": {"content": f"{period} {mapped_type} Değerlendirme"}}]},
            "Değerlendirme Tipi": {"select": {"name": mapped_type}},
            "Gerçekleştirilme Tarihi": {"date": {"start": datetime.datetime.now().strftime("%Y-%m-%d")}},
        }

        children = [
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Özet"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": summary}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Genel Değerlendirme"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": assessment}}]}}
        ]

        if wins:
            children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Kazanımlar"}}]}})
            for win in wins:
                children.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": win}}]}})

        if challenges:
            children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Zorluklar"}}]}})
            for ch in challenges:
                children.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": ch}}]}})

        if lessons_learned:
            children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Öğrenilen Dersler"}}]}})
            children.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": lessons_learned}}]}})

        if next_period_focus:
            children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Gelecek Dönem Odakları"}}]}})
            for focus in next_period_focus:
                children.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": focus}}]}})

        try:
            response = self.client.pages.create(
                parent={"database_id": self.db_ids["reviews"]},
                properties=properties,
                children=children
            )
            return response["id"]
        except Exception as e:
            print(f"Error creating review session: {e}")
            return ""

    def update_goal_progress(self, goal_id: str, status: Optional[str] = None) -> bool:
        """
        Update a goal's status in Notion.
        Note: Progress is usually a formula or rollup in Notion, so we mostly update Status.
        """
        properties = {}
        if status:
            properties["Durum"] = {"select": {"name": status}}

        if not properties:
            return True

        try:
            self.client.pages.update(page_id=goal_id, properties=properties)
            return True
        except Exception as e:
            print(f"Error updating goal {goal_id}: {e}")
            return False

    def find_goal_by_name(self, name: str) -> Optional[str]:
        """
        Find a goal ID by its exact name.
        """
        query_filter = {
            "property": "Ad",
            "title": {
                "equals": name
            }
        }
        results = self._safe_query(self.db_ids["periodic_goals"], query_filter)
        if results:
            return results[0]["id"]
        return None

    def get_journal_entry(self, date_str: str) -> Optional[Dict]:
        """
        Get the journal entry page for a specific date.
        """
        query_filter = {
            "property": "Tarih",
            "date": {
                "equals": date_str
            }
        }
        results = self._safe_query(self.db_ids["journal"], query_filter)
        if results:
            return results[0]
        return None

    # ==================== Habit Log Operations (Phase 7.2) ====================

    def create_habit_log(
        self, 
        habit_id: str, 
        date_str: str, 
        completed: bool, 
        notes: str = "", 
        journal_id: Optional[str] = None
    ) -> str:
        """
        Create a new habit log entry in Notion.
        
        Args:
            habit_id: ID of the habit being logged
            date_str: ISO date string (YYYY-MM-DD)
            completed: Whether the habit was completed (True) or skipped (False)
            notes: Optional notes about the completion
            journal_id: Optional link to the daily journal entry
            
        Returns:
            ID of the created habit log page, or empty string on error.
        """
        if not self.db_ids["habit_logs"]:
            print("Error: Habit Logs DB ID missing")
            return ""

        # Generate Tarih Kodu: "2026-01-27-HabitID"
        tarih_kodu = f"{date_str}-{habit_id[:8]}"

        properties = {
            "Tarih Kodu": {"title": [{"text": {"content": tarih_kodu}}]},
            "Alışkanlık": {"relation": [{"id": habit_id}]},
            "Tarih": {"date": {"start": date_str}},
            "Tamamlandı": {"checkbox": completed},
        }
        
        if notes:
            properties["Notlar"] = {"rich_text": [{"text": {"content": notes[:2000]}}]}
            
        if journal_id:
            properties["Günlük Günce"] = {"relation": [{"id": journal_id}]}

        try:
            response = self.client.pages.create(
                parent={"database_id": self.db_ids["habit_logs"]},
                properties=properties
            )
            return response["id"]
        except Exception as e:
            print(f"Error creating habit log: {e}")
            return ""

    def fetch_habit_logs(
        self, 
        habit_id: Optional[str] = None, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch habit logs with optional filters.
        
        Args:
            habit_id: Filter by specific habit ID
            start_date: ISO date string for range start (inclusive)
            end_date: ISO date string for range end (inclusive)
            
        Returns:
            List of habit log objects sorted by date descending.
        """
        if not self.db_ids["habit_logs"]:
            print("Error: Habit Logs DB ID missing")
            return []

        filters = []
        
        if habit_id:
            filters.append({
                "property": "Alışkanlık",
                "relation": {
                    "contains": habit_id
                }
            })
            
        if start_date:
            filters.append({
                "property": "Tarih",
                "date": {
                    "on_or_after": start_date
                }
            })
            
        if end_date:
            filters.append({
                "property": "Tarih",
                "date": {
                    "on_or_before": end_date
                }
            })
        
        query_filter = None
        if filters:
            query_filter = {"and": filters} if len(filters) > 1 else filters[0]
        
        try:
            response = self.client.databases.query(
                database_id=self.db_ids["habit_logs"],
                filter=query_filter,
                sorts=[{"property": "Tarih", "direction": "descending"}]
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Error fetching habit logs: {e}")
            return []

    def fetch_habit_logs_by_period(self, period_field: str, period_value: str) -> List[Dict]:
        """
        Fetch habit logs filtered by period (Hafta, Ay, Çeyrek, Yıl).
        
        Args:
            period_field: "Hafta", "Ay", "Çeyrek", or "Yıl"
            period_value: e.g., "2026-W02", "2026-01", "2026-Q1", "2026"
            
        Returns:
            List of habit log objects matching the period.
        """
        if not self.db_ids["habit_logs"]:
            return []

        log_filter = {
            "property": period_field,
            "formula": {
                "string": {
                    "equals": period_value
                }
            }
        }
        
        try:
            response = self.client.databases.query(
                database_id=self.db_ids["habit_logs"],
                filter=log_filter,
                sorts=[{"property": "Tarih", "direction": "descending"}]
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Error fetching habit logs by {period_field}={period_value}: {e}")
            return []

    def update_habit(
        self, 
        habit_id: str, 
        completion_rate: Optional[float] = None, 
        streak: Optional[int] = None, 
        last_completion: Optional[str] = None
    ) -> bool:
        """
        Update a habit's calculated statistics.
        
        Args:
            habit_id: ID of the habit to update
            completion_rate: Completion rate as decimal (0-1) for Notion percent field
            streak: Current consecutive completion streak
            last_completion: ISO date string of last completion
            
        Returns:
            True if successful, False otherwise.
        """
        properties = {}
        
        if completion_rate is not None:
            # Store as decimal (0-1) since Notion number properties
            properties["Tamamlama Oranı"] = {"number": completion_rate}
            
        if streak is not None:
            properties["Streak"] = {"number": streak}
            
        if last_completion:
            properties["Son Tamamlama"] = {"date": {"start": last_completion}}

        if not properties:
            return True  # Nothing to update

        try:
            self.client.pages.update(page_id=habit_id, properties=properties)
            return True
        except Exception as e:
            print(f"Error updating habit {habit_id}: {e}")
            return False
