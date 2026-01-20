import click
import os
import sys
import subprocess
import datetime

# Add current directory to path so relative imports work if run as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.context_generator import ContextGenerator
from orchestration.journal_service import JournalService
from orchestration.review_service import ReviewService
from orchestration.habit_service import HabitService
from orchestration.goal_service import GoalService

def notify(title, message):
    """Send a macOS notification."""
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(['osascript', '-e', script])
    except Exception:
        pass

@click.group()
def cli():
    """PersonalAxis: AI-Powered Life OS Orchestration Layer."""
    pass

@cli.command()
@click.option('--notify', 'do_notify', is_flag=True, help="Send a macOS notification when finished")
def daily_context(do_notify):
    """Generate daily context for Gemini/AI coaching."""
    try:
        generator = ContextGenerator()
        file_path = generator.generate_daily_context()
        click.echo(f"Success! Context is ready at: {file_path}")
        if do_notify:
            notify("PersonalAxis", "Daily context generation completed.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if do_notify:
            notify("PersonalAxis Error", f"Daily context failed: {str(e)[:50]}")

@cli.command()
@click.option('--title', prompt="Journal Title (e.g., 2026-01-11)", help="The title for the journal entry")
@click.option('--date', 'date_str', help="ISO date string (YYYY-MM-DD). Defaults to today.")
def save_journal(title, date_str):
    """Save a journal entry from Gemini output."""
    click.echo("Paste the Gemini summary below (press Ctrl-D or Ctrl-Z on Windows to finish):")
    raw_content = sys.stdin.read()
    
    if not raw_content.strip():
        click.echo("Aborted: No content provided.")
        return

    try:
        journal_service = JournalService()
        if journal_service.save_journal(title, raw_content, date_str):
            click.echo("Successfully saved journal and tasks!")
        else:
            click.echo("Failed to save journal.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option('--type', 'review_type', type=click.Choice(['weekly', 'monthly', 'quarterly', 'yearly']), required=True)
@click.option('--period', help="e.g., 2026-W1, 2026-01, or 'last' for previous period. Defaults to current.")
@click.option('--notify', 'do_notify', is_flag=True, help="Send a macOS notification when finished")
def review_context(review_type, period, do_notify):
    """Generate periodic review context for AI."""
    try:
        generator = ContextGenerator()
        file_path = generator.generate_review_context(review_type, period)
        click.echo(f"Success! {review_type.capitalize()} review context is ready at: {file_path}")
        if do_notify:
            notify("PersonalAxis", f"{review_type.capitalize()} review context ready.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if do_notify:
            notify("PersonalAxis Error", f"{review_type.capitalize()} review failed.")

@cli.command()
@click.argument('content', required=False)
def quick_journal(content):
    """Quick journal entry. If content is not provided, opens stdin."""
    if not content:
        click.echo("Enter your journal entry (press Ctrl-D to finish):")
        content = sys.stdin.read()
    
    if not content.strip():
        click.echo("Aborted: No content.")
        return

    try:
        from orchestration.notion_service import NotionClient
        client = NotionClient()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        title = f"Quick Entry {datetime.datetime.now().strftime('%H:%M')}"
        
        # We'll use create_journal_entry but with minimal AI processing
        page_id = client.create_journal_entry(
            date_str=today,
            title=title,
            content=content,
            insights="Manual quick entry"
        )
        if page_id:
            click.echo(f"Successfully saved quick journal entry!")
        else:
            click.echo("Failed to save entry.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
def goal_status():
    """Summary of active goals' progress."""
    try:
        goal_service = GoalService()
        goals = goal_service.get_active_goals()
        
        click.echo("\n--- Aktif Hedefler ---")
        if not goals:
            click.echo("Aktif hedef bulunamadı.")
        else:
            for g in goals:
                name = g["properties"]["Ad"]["title"][0]["plain_text"]
                # Progress is usually a formula/rollup, we might not have 'Progress' property directly if it's complex
                # But let's check for 'Durum' or 'İlerleme'
                status = g["properties"].get("Durum", {}).get("select", {}).get("name", "N/A")
                click.echo(f"• {name} [{status}]")
        click.echo("")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
def habits():
    """Show today's habit checklist (Sync from Notion)."""
    try:
        habit_service = HabitService()
        habits = habit_service.get_todays_habits()
        
        click.echo("\n--- Bugünkü Alışkanlıklar ---")
        if not habits:
            click.echo("Aktif alışkanlık bulunamadı.")
        else:
            for h in habits:
                name = h["properties"]["Ad"]["title"][0]["plain_text"]
                freq = h["properties"]["Frekans"]["select"]["name"]
                click.echo(f"☐ {name} ({freq})")
        click.echo("")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option('--type', 'review_type', type=click.Choice(['weekly', 'monthly', 'quarterly', 'yearly']), required=True)
@click.option('--period', help="e.g., 2026-W1, 2026-01. Defaults to current period.")
def save_review(review_type, period):
    """Save a periodic review session from ChatGPT output."""
    click.echo(f"Paste the ChatGPT {review_type} summary (JSON) below (press Ctrl-D or Ctrl-Z to finish):")
    raw_content = sys.stdin.read()
    
    if not raw_content.strip():
        click.echo("Aborted: No content provided.")
        return

    try:
        review_service = ReviewService()
        if review_service.save_review(review_type, period, raw_content):
            click.echo("Successfully saved review and updated goals!")
        else:
            click.echo("Failed to save review.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    cli()
