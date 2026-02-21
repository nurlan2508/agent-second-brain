#!/usr/bin/env python3
"""Daily GTD processing script for VPS cron execution."""

import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/d-brain-daily.log')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Run daily GTD processing."""
    today = date.today()
    logger.info("="*60)
    logger.info(f"Starting daily GTD processing for {today}")
    logger.info("="*60)
    
    try:
        # Add src to path for imports
        project_root = Path(__file__).parent.parent.parent.parent
        src_path = project_root / 'src'
        sys.path.insert(0, str(src_path))
        
        from d_brain.services.session import SessionStore
        from d_brain.services.claude_api_processor import ClaudeAPIProcessor
        from d_brain.config import Settings
        
        # Load settings
        settings = Settings(_env_file=project_root / '.env')
        logger.info(f"✓ Settings loaded from {project_root / '.env'}")
        logger.info(f"  Vault path: {settings.vault_path}")
        logger.info(f"  Daily path: {settings.daily_path}")
        
        # Get today's entries
        session = SessionStore(settings.vault_path)
        today_entries = session.get_today(0)  # user_id=0 for system processing
        
        if not today_entries:
            logger.info("No entries captured today")
            logger.info("="*60)
            return
        
        logger.info(f"Found {len(today_entries)} entries to process")
        
        # Process each entry
        processor = ClaudeAPIProcessor(
            settings.vault_path,
            str(settings.google_credentials_path)
        )
        
        results = {
            'total': len(today_entries),
            'tasks': 0,
            'notes': 0,
            'waiting': 0,
            'someday': 0,
            'errors': 0
        }
        
        for i, entry in enumerate(today_entries, 1):
            text = entry.get('text', '').strip()
            if not text:
                continue
            
            logger.info(f"\n[{i}/{len(today_entries)}] Processing: {text[:50]}...")
            
            try:
                result = processor.process_entry(text, user_id=0)
                
                # Track results
                entry_type = result.get('type', 'unknown')
                if entry_type == 'task':
                    results['tasks'] += 1
                elif entry_type == 'note':
                    results['notes'] += 1
                elif entry_type == 'waiting':
                    results['waiting'] += 1
                elif entry_type == 'someday':
                    results['someday'] += 1
                elif entry_type == 'error':
                    results['errors'] += 1
                
                status = result.get('status', 'Unknown')
                logger.info(f"  ✓ {entry_type.upper()}: {status}")
                
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                results['errors'] += 1
        
        # Log summary
        logger.info("\n" + "="*60)
        logger.info("Processing Summary:")
        logger.info(f"  Total entries: {results['total']}")
        logger.info(f"  Tasks created: {results['tasks']}")
        logger.info(f"  Notes created: {results['notes']}")
        logger.info(f"  Waiting items: {results['waiting']}")
        logger.info(f"  Someday items: {results['someday']}")
        logger.info(f"  Errors: {results['errors']}")
        logger.info("="*60)
        
        return results
        
    except Exception as e:
        logger.exception(f"Fatal error during processing: {e}")
        return None


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)
