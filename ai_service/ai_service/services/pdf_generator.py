# ai_service/services/pdf_generator.py
import os
from fpdf import FPDF
from typing import Dict, List, Any
import datetime

# --- Annotation [services/pdf_generator.py: 1] ---
# Define constants for styling (optional but good practice)
FONT_FAMILY = "DejaVu" # Use the font installed in Dockerfile
FONT_STYLE_NORMAL = ""
FONT_STYLE_BOLD = "B"
FONT_SIZE_TITLE = 16
FONT_SIZE_HEADING = 12
FONT_SIZE_NORMAL = 10
LINE_HEIGHT_MULTIPLIER = 1.5 # Adjust spacing between lines


DEJAVU_FONT_PATH_DIR = "/usr/share/fonts/truetype/dejavu/"
DEJAVU_FONT_REGULAR = os.path.join(DEJAVU_FONT_PATH_DIR, 'DejaVuSans.ttf')
DEJAVU_FONT_BOLD = os.path.join(DEJAVU_FONT_PATH_DIR, 'DejaVuSans-Bold.ttf')


class PDFResumeGenerator:

    def __init__(self):
        global FONT_FAMILY # Allow modification of FONT_FAMILY on fallback
        self.pdf = FPDF('P', 'mm', 'A4')

        # --- MODIFICATION START ---
        # Check if the font files actually exist before trying to add them
        font_regular_exists = os.path.exists(DEJAVU_FONT_REGULAR)
        font_bold_exists = os.path.exists(DEJAVU_FONT_BOLD)

        if font_regular_exists and font_bold_exists:
            try:
                # Provide the full path to add_font
                self.pdf.add_font(FONT_FAMILY, '', DEJAVU_FONT_REGULAR, uni=True)
                self.pdf.add_font(FONT_FAMILY, FONT_STYLE_BOLD, DEJAVU_FONT_BOLD, uni=True)
                print(f"Successfully loaded DejaVu fonts from {DEJAVU_FONT_PATH_DIR}") # Added log
            except RuntimeError as e:
                print(f"Error loading DejaVu font even though files exist: {e}. Falling back.")
                FONT_FAMILY = "Arial" # Fallback
        else:
            # Log which file is missing
            if not font_regular_exists:
                 print(f"Warning: Font file not found at {DEJAVU_FONT_REGULAR}")
            if not font_bold_exists:
                 print(f"Warning: Font file not found at {DEJAVU_FONT_BOLD}")
            print("Falling back to default Arial font.")
            print("Ensure 'fonts-dejavu-core' is installed correctly in the Docker image and the path is correct.")
            FONT_FAMILY = "Arial" # Fallback
        # --- MODIFICATION END ---

        self.pdf.add_page()
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_NORMAL)
        self.line_height = FONT_SIZE_NORMAL * LINE_HEIGHT_MULTIPLIER

    def _add_section_heading(self, title: str):
        # --- Annotation [services/pdf_generator.py: 7] ---
        # Helper method to add a styled section heading.
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_HEADING)
        self.pdf.cell(0, self.line_height * 1.5, title, ln=1, align='L') # Add extra space before heading
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_NORMAL) # Reset font
        self.pdf.ln(self.line_height / 2) # Add some space after heading

    def _add_qa(self, question: str, answer: str):
        # --- Annotation [services/pdf_generator.py: 8] ---
        # Helper method to add a Question-Answer pair.
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_NORMAL)
        self.pdf.multi_cell(0, self.line_height, f"Q: {question}", ln=1)
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_NORMAL)
        self.pdf.multi_cell(0, self.line_height, f"A: {answer}", ln=1)
        self.pdf.ln(self.line_height / 2) # Add space after Q/A pair

    def _add_list_items(self, items: List[str]):
        # --- Annotation [services/pdf_generator.py: 9] ---
        # Helper method to add items as a bulleted list.
        if not items:
            self.pdf.multi_cell(0, self.line_height, "N/A", ln=1)
            return
        for item in items:
            # Use a simple dash as bullet point
            self.pdf.multi_cell(0, self.line_height, f"- {item}", ln=1)
        self.pdf.ln(self.line_height / 2) # Add space after the list

    def generate(self, user_answers: Dict[str, str], generated_skills: List[str]) -> bytes:
        # --- Annotation [services/pdf_generator.py: 10] ---
        # Main method to orchestrate the PDF creation.
        # Takes user answers and the processed skills list as input.

        # --- Title ---
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_TITLE)
        self.pdf.cell(0, self.line_height * 2, "Resume Summary", ln=1, align='C')
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_NORMAL)
        self.pdf.ln(self.line_height)

        # --- Generated Skills Section ---
        # --- Annotation [services/pdf_generator.py: 11] ---
        # Add the most important output: the generated skills.
        self._add_section_heading("Generated Hard Skills")
        self._add_list_items(generated_skills)

        # --- Raw Answers Section ---
        # --- Annotation [services/pdf_generator.py: 12] ---
        # Optionally include the raw answers provided by the user for context.
        self._add_section_heading("User Provided Answers")
        if user_answers:
            for question, answer in user_answers.items():
                self._add_qa(question, answer)
        else:
            self.pdf.multi_cell(0, self.line_height, "No answers provided.", ln=1)

        # --- Footer (Optional) ---
        # You could add generation date, etc. here
        self.pdf.set_y(-15) # Position 15 mm from bottom
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, 8)
        self.pdf.cell(0, 10, f"Generated on: {datetime.date.today().strftime('%Y-%m-%d')}", 0, 0, 'C')

        # --- Annotation [services/pdf_generator.py: 13] ---
        # Output the PDF content as bytes.
        # FPDF.output() with no 'name' argument returns bytes directly.
        return self.pdf.output()

# --- Annotation [services/pdf_generator.py: 14] ---
# Define a function to be easily called from the router.
# This creates an instance of the generator and calls its generate method.
def create_resume_pdf(user_answers: Dict[str, str], generated_skills: List[str]) -> bytes:
    """
    Creates a resume summary PDF from user answers and generated skills.

    Args:
        user_answers: Dictionary of question-answer pairs.
        generated_skills: List of hard skills generated by the AI.

    Returns:
        bytes: The generated PDF content.
    """
    generator = PDFResumeGenerator()
    pdf_bytes = generator.generate(user_answers, generated_skills)
    return pdf_bytes
