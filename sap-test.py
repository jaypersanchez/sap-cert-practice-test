import tkinter as tk
from tkinter import messagebox
from docx import Document
import random
import openai
import os
from dotenv import load_dotenv
import tkinter as tk

# Load the OpenAI API key from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# Function to parse questions from the Practice Test Document
def parse_questions(doc_path):
    doc = Document(doc_path)
    questions = []
    question = {}
    for para in doc.paragraphs:
        if para.text.startswith("Q"):
            if question and question['options']:  # Only append if there are options
                questions.append(question)
            # Check for matching questions
            if "match the following" in para.text.lower():
                question = {}  # Reset question to skip it
            else:
                question = {'question': para.text.replace("?", ""), 'options': [], 'answer': '', 'explanation': '', 'type': 'standard'}
        elif para.text.startswith("A.") or para.text.startswith("B.") or para.text.startswith("C.") or para.text.startswith("D."):
            if question:  # Only add options if a question is being built
                question['options'].append(para.text)
        elif para.text.startswith("Answer:"):
            if question:  # Only set answer if a question is being built
                question['answer'] = para.text.split(":")[1].strip().lower()  # Store answer in lowercase for consistency
        elif para.text.startswith("Referenced from"):
            if question:  # Only set explanation if a question is being built
                question['explanation'] = para.text
    # Add the last question if it has options
    if question and question['options']:
        questions.append(question)
    return questions

# Function to load study references from the condensed notes document
def load_references_from_notes(notes_path):
    doc = Document(notes_path)
    references = []
    for para in doc.paragraphs:
        if para.text:
            references.append(para.text)
    return references

# Function to get random questions
def get_random_questions(questions, num=5):
    return random.sample(questions, num)

# Main GUI Application
class PracticeTestApp:
    def __init__(self, master, questions, references):
        self.master = master
        self.master.title("SAP Certification Practice Test")
        self.questions = get_random_questions(questions)
        self.references = references
        self.current_question = 0
        self.user_answers = []

        # Question Label
        self.question_label = tk.Label(master, text="", wraplength=400, justify="left")
        self.question_label.pack(pady=20)

        # Options Radio Buttons
        self.options_var = tk.StringVar()
        self.option_buttons = []
        for i in range(4):  # Assuming 4 options (A, B, C, D)
            btn = tk.Radiobutton(master, text="", variable=self.options_var, value=i, wraplength=400, anchor='w', justify="left")
            btn.pack(anchor='w', pady=5)
            self.option_buttons.append(btn)

        # Next Button
        self.next_button = tk.Button(master, text="Next", command=self.next_question)
        self.next_button.pack(pady=20)

        self.load_question()

    def load_question(self):
        # Load current question into the interface
        q = self.questions[self.current_question]
        self.question_label.config(text=q['question'])

        for i, option in enumerate(q['options']):
            self.option_buttons[i].config(text=option)
        self.options_var.set(None)  # Reset selection

    def next_question(self):
        if self.options_var.get() is None:
            messagebox.showwarning("No selection", "Please select an answer before proceeding.")
            return

        # Save user's answer
        self.user_answers.append(self.options_var.get())
        self.current_question += 1

        # Check if the test is complete
        if self.current_question < len(self.questions):
            self.load_question()
        else:
            self.show_results()  # Ensure this method is defined in the class

    def get_chatgpt_explanation(self, prompt):
        """Function to send prompt to OpenAI API and get a response."""
        try:
            # Using the new ChatCompletion API with gpt-3.5-turbo or gpt-4
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # You can switch to "gpt-4" if needed
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,  # Adjust token count based on needs
                temperature=0.7
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error: {str(e)}"


    # Method to show results and fetch detailed explanations from ChatGPT
    def show_results(self):
        correct = 0
        results_window = tk.Toplevel(self.master)
        results_window.title("Results")

        # Create a Text widget to display results on the left side (60% width)
        result_text_widget = tk.Text(results_window, wrap="word", width=50, height=20)
        result_text_widget.grid(row=0, column=0, padx=10, pady=20)

        # Create another Text widget for ChatGPT explanations on the right side (40% width)
        chatgpt_response_widget = tk.Text(results_window, wrap="word", width=40, height=20)
        chatgpt_response_widget.grid(row=0, column=1, padx=10, pady=20)

        # Evaluate answers and build the result summary
        result_summary = "Quiz Results:\n"
        for i, q in enumerate(self.questions):
            selected = self.user_answers[i]
            correct_answer = q['answer']  # The correct answer is a string, e.g., 'b'
            question_text = q['question']  # Store the original question

            # Determine the index of the correct option
            correct_option = None
            for j, option in enumerate(q['options']):
                if option.lower().startswith(correct_answer):
                    correct_option = j
                    break

            selected_option_text = q['options'][int(selected)]  # Get the full text of the selected option
            correct_option_text = q['options'][correct_option]  # Get the full text of the correct option

            # Add to result summary
            result_summary += f"Q{i + 1}. {question_text}\n"
            if int(selected) == correct_option:
                correct += 1
                result_summary += f"Your Answer: {selected_option_text} (Correct)\n\n"
            else:
                result_summary += f"Your Answer: {selected_option_text} (Wrong)\n"
                result_summary += f"Correct Answer: {correct_option_text} (Correct)\n\n"

        # Insert the result summary into the Text widget
        result_text_widget.insert(tk.END, result_summary)

        # Show the final score
        score_text = f"Your Score: {correct}/{len(self.questions)}\n\n"
        result_text_widget.insert(tk.END, score_text)

        # Configure tags to color text (optional)
        result_text_widget.tag_config('wrong', foreground="red")
        result_text_widget.tag_config('correct', foreground="green")

        # Make the Text widget read-only
        result_text_widget.config(state=tk.DISABLED)

        # Prepare the prompt to be sent to ChatGPT
        prompt = f"{result_summary}\n\nCan you provide elaborate explanation for each answer, even if they are right or wrong? This will enhance the student's learning through the practice test."

        # Fetch the explanation from ChatGPT
        chatgpt_explanation = self.get_chatgpt_explanation(prompt)

        # Insert the response into the right-side Text widget
        chatgpt_response_widget.insert(tk.END, chatgpt_explanation)
        chatgpt_response_widget.config(state=tk.DISABLED)

        # OK Button to close the results window
        ok_button = tk.Button(results_window, text="OK", command=results_window.destroy)
        ok_button.grid(row=1, column=0, columnspan=2, pady=10)


# Main function to start the application
def main():
    # Parse the questions and references
    questions = parse_questions("PracticeTestChatGptGenerated.docx")
    references = load_references_from_notes("CondensedStudyNotesforCertification.docx")

    # Start the GUI
    root = tk.Tk()
    app = PracticeTestApp(root, questions, references)
    root.mainloop()

# Run the application
if __name__ == "__main__":
    main()
