import sqlite3

def clear_database(db_name):
    """Clear all data from the questions and study_references tables in the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # Clear all data from the questions table
        cursor.execute("DELETE FROM questions")
        # Clear all data from the study_references table
        cursor.execute("DELETE FROM study_references")
        
        conn.commit()
        print("All data has been successfully cleared from the database.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    db_name = 'questions.db'  # Database name
    clear_database(db_name) 