#!/usr/bin/env python3
"""
Database migration script to add cat support to existing dog voting database
"""

import sqlite3
import sys

def migrate_database():
    """Add new columns for cat support to existing database"""
    try:
        conn = sqlite3.connect('dog_voting.db')
        cursor = conn.cursor()
        
        print("🔄 Checking current database schema...")
        
        # Check if is_cat column exists
        cursor.execute("PRAGMA table_info(dogs)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        if 'is_cat' not in columns:
            print("➕ Adding 'is_cat' column...")
            cursor.execute('ALTER TABLE dogs ADD COLUMN is_cat BOOLEAN DEFAULT FALSE')
            
        if 'cat_votes' not in columns:
            print("➕ Adding 'cat_votes' column...")
            cursor.execute('ALTER TABLE dogs ADD COLUMN cat_votes INTEGER DEFAULT 0')
        
        # Create cat_votes table if it doesn't exist
        print("🐱 Creating cat_votes table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cat_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dog_id INTEGER,
                vote_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dog_id) REFERENCES dogs (id)
            )
        ''')
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(dogs)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"✅ Updated columns: {new_columns}")
        
        print("🎉 Database migration completed successfully!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1) 