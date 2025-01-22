import sqlite3

def view_all_tables(db_name):
    """Retrieve and display all table names in the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables in the Database:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()

def view_all_questions(db_name):
    """Retrieve and display all questions from the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM questions")
    rows = cursor.fetchall()
    
    print("All Questions in the Database:")
    for row in rows:
        print(f"ID: {row[0]}, Subject: {row[1]}, Question: {row[2]}, Options: {row[3]}, Answer: {row[4]}, Explanation: {row[5]}, Tags: {row[6]}")
    
    conn.close()

def view_questions_by_subject(db_name, subject):
    """Retrieve and display questions for a specific subject."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM questions WHERE subject = ?", (subject,))
    rows = cursor.fetchall()
    
    if rows:
        print(f"Questions for Subject: {subject}")
        for row in rows:
            print(f"ID: {row[0]}, Question: {row[2]}, Options: {row[3]}, Answer: {row[4]}, Explanation: {row[5]}, Tags: {row[6]}")
    else:
        print(f"No questions found for subject: {subject}")
    
    conn.close()

def run_custom_query(db_name, query):
    """Run a custom SQL query and display the results."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        else:
            conn.commit()
            print("Query executed successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    db_name = 'questions.db'  # Database name
    
    # View all tables
    view_all_tables(db_name)
    
    # View all questions
    view_all_questions(db_name)
    
    # Example: View questions for a specific subject
    subject_to_view = input("Enter the subject to view questions (or press Enter to skip): ")
    if subject_to_view:
        view_questions_by_subject(db_name, subject_to_view)

    # Run custom SQL queries
    while True:
        custom_query = input("Enter a SQL statement to execute (or type 'exit' to quit): ")
        if custom_query.lower() == 'exit':
            break
        run_custom_query(db_name, custom_query)
