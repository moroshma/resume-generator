# ai_service/services/pdf_generator.py

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

class PDFResumeGenerator:

    def __init__(self):
        # --- Annotation [services/pdf_generator.py: 2] ---
        # Initialize FPDF object. 'P' for portrait, 'mm' for units, 'A4' for size.
        self.pdf = FPDF('P', 'mm', 'A4')
        # --- Annotation [services/pdf_generator.py: 3] ---
        # Add the DejaVu font. Required for Unicode characters like Cyrillic.
        # The .ttf file should be available in the system paths after installation via apt-get.
        # Use the regular, bold, italic, bold-italic variants if needed.
        # We'll just use Regular and Bold here.
        try:
            self.pdf.add_font(FONT_FAMILY, '', 'DejaVuSans.ttf', uni=True)
            self.pdf.add_font(FONT_FAMILY, FONT_STYLE_BOLD, 'DejaVuSans-Bold.ttf', uni=True)
        except RuntimeError as e:
            print(f"Warning: Could not load DejaVu font ({e}). Falling back to default Arial.")
            print("Ensure 'fonts-dejavu-core' is installed in the Docker image.")
            # Fallback to a standard font if DejaVu isn't found (may not support Cyrillic well)
            global FONT_FAMILY
            FONT_FAMILY = "Arial"
            # Arial is usually built-in, no add_font needed unless variants are missing

        # --- Annotation [services/pdf_generator.py: 4] ---
        # Add the first page automatically.
        self.pdf.add_page()
        # --- Annotation [services/pdf_generator.py: 5] ---
        # Set default font for the document.
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_NORMAL)
        # --- Annotation [services/pdf_generator.py: 6] ---
        # Calculate line height based on font size for consistent spacing.
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
