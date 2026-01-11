import click
import os
import sys

# Add current directory to path so relative imports work if run as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.context_generator import ContextGenerator

@click.group()
def cli():
    """PersonalAxis: AI-Powered Life OS Orchestration Layer."""
    pass

@cli.command()
def daily_context():
    """Generate daily context for Gemini/AI coaching."""
    try:
        generator = ContextGenerator()
        file_path = generator.generate_daily_context()
        click.echo(f"Success! Context is ready at: {file_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

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
        generator = ContextGenerator()
        if generator.save_journal(title, raw_content, date_str):
            click.echo("Successfully saved journal and tasks!")
        else:
            click.echo("Failed to save journal.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option('--type', 'review_type', type=click.Choice(['weekly', 'monthly', 'quarterly', 'yearly']), required=True)
@click.option('--period', required=True, help="e.g., 2026-W1, 2026-01, 2026-Q1, 2026")
def review_context(review_type, period):
    """Generate periodic review context for ChatGPT."""
    try:
        generator = ContextGenerator()
        file_path = generator.generate_review_context(review_type, period)
        click.echo(f"Success! {review_type.capitalize()} review context is ready at: {file_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
def habits():
    """Show today's habit checklist (Sync from Notion)."""
    try:
        from orchestration.notion_client import NotionClient
        client = NotionClient()
        habits = client.fetch_active_habits()
        
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

if __name__ == "__main__":
    cli()
