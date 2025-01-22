import os
import database

def insert_questions_and_references_from_subfolders(base_dir, db_name):
    # Create the database and tables
    database.create_database(db_name)

    # Walk through all subdirectories in the base directory
    for root, dirs, files in os.walk(base_dir):
        subject = os.path.basename(root)  # Get the name of the current folder as the subject
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check the file extension and parse accordingly
            if file.endswith('.docx'):
                print(f"Inserting questions from {file_path} for subject '{subject}'")
                database.parse_and_insert_questions(db_name, subject, file_path)
                
                # Load references from notes.docx
                notes_path = os.path.join(root, 'notes.docx')  # Assuming notes file is named 'notes.docx'
                if os.path.exists(notes_path):
                    print(f"Loading references from {notes_path} for subject '{subject}'")
                    database.load_references_from_notes(db_name, subject, notes_path)
                    
            elif file.endswith('.pdf'):
                print(f"Inserting questions from {file_path} for subject '{subject}'")
                database.parse_and_insert_questions(db_name, subject, file_path)
                
                # Load references from notes.pdf
                notes_path = os.path.join(root, 'notes.pdf')  # Assuming notes file is named 'notes.pdf'
                if os.path.exists(notes_path):
                    print(f"Loading references from {notes_path} for subject '{subject}'")
                    database.load_references_from_notes(db_name, subject, notes_path)

if __name__ == "__main__":
    base_directory = 'contents'  # Base directory containing subfolders
    db_name = 'questions.db'  # Database name
    insert_questions_and_references_from_subfolders(base_directory, db_name)
    print("All questions and references have been successfully inserted into the database.")