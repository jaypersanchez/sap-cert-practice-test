import argparse
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from docx import Document
import random
import os
import pickle
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import sqlite3

# Load the OpenAI API key from the .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ----------------------------
# Database Functions
# ----------------------------

def load_subjects(db_name):
    """Load all distinct subjects from the questions table."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT subject FROM questions")
    subjects = cursor.fetchall()
    
    conn.close()
    return [subject[0] for subject in subjects]  # Extracting the subject names

def load_questions(db_name, subject):
    """Load questions from the database for a specific subject."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM questions WHERE LOWER(subject) = LOWER(?)", (subject,))
    questions = cursor.fetchall()
    
    conn.close()
    return questions

def load_references(db_name, subject):
    """Load references for a specific subject."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT reference FROM study_references WHERE subject = ?", (subject,))
    references = cursor.fetchall()
    
    conn.close()
    return [ref[0] for ref in references]  # Extracting the reference text

# ----------------------------
# Main GUI Application
# ----------------------------

class SubjectSelectionApp:
    def __init__(self, master, db_name):
        self.master = master
        self.master.title("Select Subject")
        
        self.db_name = db_name
        self.subjects = load_subjects(db_name)
        
        self.label = tk.Label(master, text="Select a subject for the test:")
        self.label.pack(pady=10)
        
        self.subject_var = tk.StringVar()
        self.subject_combobox = ttk.Combobox(master, textvariable=self.subject_var, values=self.subjects)
        self.subject_combobox.pack(pady=10)
        
        self.test_type_var = tk.StringVar(value="Preview")  # Default to Preview
        self.test_type_label = tk.Label(master, text="Select test type:")
        self.test_type_label.pack(pady=10)
        
        self.preview_radio = tk.Radiobutton(master, text="Preview (10 questions)", variable=self.test_type_var, value="Preview")
        self.preview_radio.pack(anchor='w')
        
        self.practice_radio = tk.Radiobutton(master, text="Practice (25 questions)", variable=self.test_type_var, value="Practice")
        self.practice_radio.pack(anchor='w')
        
        self.certified_radio = tk.Radiobutton(master, text="Certified Simulation (All questions)", variable=self.test_type_var, value="Certified")
        self.certified_radio.pack(anchor='w')
        
        self.select_button = tk.Button(master, text="Start Test", command=self.start_test)
        self.select_button.pack(pady=20)
    
    def start_test(self):
        selected_subject = self.subject_var.get()
        if not selected_subject:
            messagebox.showwarning("No Subject Selected", "Please select a subject.")
            return
        
        # Load questions for the selected subject
        questions = load_questions(self.db_name, selected_subject)  # Load questions for the selected subject
        references = load_references(self.db_name, selected_subject)  # Load references for the selected subject
        
        # Determine the number of questions based on the selected test type
        test_type = self.test_type_var.get()
        if test_type == "Preview":
            questions = random.sample(questions, min(10, len(questions)))  # 10 random questions
        elif test_type == "Practice":
            questions = random.sample(questions, min(25, len(questions)))  # 25 random questions
        elif test_type == "Certified":
            questions = questions  # All questions
        
        # Open the test window without destroying the main window
        self.open_test_window(questions, references)
    
    def open_test_window(self, questions, references):
        test_window = tk.Toplevel(self.master)
        app = PracticeTestApp(test_window, questions, references)

class PracticeTestApp:
    def __init__(self, master, questions, references):
        self.master = master
        self.master.title("Practice Test")
        
        self.questions = questions
        self.references = references
        self.current_question = 0
        self.user_answers = []
        
        # GUI Widgets
        self.question_label = tk.Label(master, text="", wraplength=800, justify="left")
        self.question_label.pack(pady=20)
        
        self.question_count_label = tk.Label(master, text="", wraplength=800, justify="left")
        self.question_count_label.pack(pady=5)

        self.options_var = tk.StringVar()
        self.option_buttons = []
        
        self.next_button = tk.Button(master, text="Next", command=self.next_question)
        self.next_button.pack(pady=20)
        
        self.load_question()
    
    def load_question(self):
        if self.current_question >= len(self.questions):
            messagebox.showerror("Error", "No more questions available.")
            return
        q = self.questions[self.current_question]
        self.question_label.config(text=q[2])  # Question text
        options = q[3].split(', ')  # Assuming options are stored as a comma-separated string
        
        # Clear existing option buttons
        for btn in self.option_buttons:
            btn.pack_forget()  # Remove the button from the window

        # Create new option buttons based on the number of options
        self.option_buttons = []  # Reset the option buttons list
        for i, option in enumerate(options):
            btn = tk.Radiobutton(self.master, text=option, variable=self.options_var, value=i, wraplength=800, anchor='w', justify="left")
            btn.pack(anchor='w', pady=5)
            self.option_buttons.append(btn)

        # Reset the selected option to None
        self.options_var.set(None)  # Clear any previous selection
        
        # Update the question count label
        self.question_count_label.config(text=f"Question {self.current_question + 1} of {len(self.questions)}")
    
    def next_question(self):
        if self.options_var.get() is None:
            messagebox.showwarning("No selection", "Please select an answer before proceeding.")
            return
        self.user_answers.append(self.options_var.get())
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.load_question()
        else:
            self.show_results()
    
    def show_results(self):
        correct = 0
        results_window = tk.Toplevel(self.master)
        results_window.title("Results")
        
        result_text_widget = tk.Text(results_window, wrap="word", width=50, height=20)
        result_text_widget.grid(row=0, column=0, padx=10, pady=20)

        # Define tags for coloring
        result_text_widget.tag_config("correct", foreground="green")
        result_text_widget.tag_config("wrong", foreground="red")

        result_summary = "Quiz Results:\n"
        for i, q in enumerate(self.questions):
            selected = self.user_answers[i]
            correct_answer = q[4]  # Assuming the correct answer is stored in the 5th column
            question_text = q[2]
            
            selected_option_text = q[3].split(', ')[int(selected)]  # Get the selected option text
            correct_option_text = correct_answer  # Assuming the correct answer is stored as a single letter
            
            # Extract only the letter from the selected option
            selected_letter = selected_option_text.split('.')[0].strip().lower()  # Get the letter part and convert to lowercase
            correct_letter = correct_option_text.strip().lower()  # Convert correct answer to lowercase
            
            result_text_widget.insert(tk.END, f"Q{i + 1}. {question_text}\n")
            if selected_letter == correct_letter:
                correct += 1
                result_text_widget.insert(tk.END, f"Your Answer: {selected_option_text} (Correct)\n\n", "correct")
                result_summary += f"Q{i + 1}: Correct\nYour Answer: {selected_option_text}\n"
            else:
                result_text_widget.insert(tk.END, f"Your Answer: {selected_option_text} (Wrong)\n", "wrong")
                result_text_widget.insert(tk.END, f"Correct Answer: {correct_option_text} (Correct)\n\n", "correct")
                result_summary += f"Q{i + 1}: Wrong\nYour Answer: {selected_option_text}\nCorrect Answer: {correct_option_text}\n"
            
            # Get explanation from OpenAI
            explanation = self.get_explanation(question_text, correct_option_text)
            result_text_widget.insert(tk.END, f"Explanation: {explanation}\n\n")
            
            # Load references for the topic
            topic = q[1]  # Assuming the topic is in the second column
            references = load_references(self.db_name, topic)
            if references:
                result_text_widget.insert(tk.END, "References:\n" + "\n".join(references) + "\n\n")
            else:
                # Prompt to add a new reference
                add_reference = messagebox.askyesno("Add Reference", f"No references found for '{topic}'. Would you like to add one?")
                if add_reference:
                    self.add_reference(topic)

        score_text = f"Your Score: {correct}/{len(self.questions)}\n\n"
        result_text_widget.insert(tk.END, score_text)
        result_summary += score_text
        result_text_widget.config(state=tk.DISABLED)
        
        # Show references for the subject
        references_text = "\nReferences:\n" + "\n".join(self.references)
        result_text_widget.insert(tk.END, references_text)
        
        ok_button = tk.Button(results_window, text="OK", command=results_window.destroy)
        ok_button.grid(row=1, column=0, columnspan=2, pady=10)

    def add_reference(self, topic):
        """Prompt user to add a new reference for the given topic."""
        new_reference = simpledialog.askstring("Add Reference", f"Enter a new reference for '{topic}':")
        if new_reference:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO study_references (subject, reference) VALUES (?, ?)", (topic, new_reference))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Reference added successfully!")

    def get_explanation(self, question, correct_answer):
        """Get explanation from OpenAI API using direct API call."""
        prompt = f"Explain why the answer '{correct_answer}' is correct for the following question: {question}"
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",  # or any other model you prefer
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            explanation = response.json()['choices'][0]['message']['content']
            return explanation
        else:
            return "Error retrieving explanation from OpenAI API."

# ----------------------------
# Main Function
# ----------------------------

def main():
    db_name = 'questions.db'  # Database name
    root = tk.Tk()
    app = SubjectSelectionApp(root, db_name)
    root.mainloop()

if __name__ == "__main__":
    main()