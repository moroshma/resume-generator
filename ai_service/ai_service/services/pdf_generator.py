# ai_service/services/pdf_generator.py
import os
from fpdf import FPDF
from typing import Dict, List, Any, Tuple
import datetime
import re
import logging

# --- Constants ---
FONT_FAMILY = "DejaVu"
FONT_STYLE_NORMAL = ""
FONT_STYLE_BOLD = "B"
FONT_SIZE_NAME = 18
FONT_SIZE_CONTACT = 10
FONT_SIZE_LABEL = 11 # Размер для лейблов
FONT_SIZE_VALUE = 10 # Размер для значений
LINE_HEIGHT_MULTIPLIER = 1.4
HEADER_FIELDS = { # Ключевые слова для поиска полей шапки (в нижнем регистре)
    "name": ["фио", "полное имя", "имя", "full name", "name"],
    "email": ["почта", "email", "e-mail"],
    "phone": ["телефон", "phone", "номер телефона", "contact number"]
}
HEADER_SEPARATOR = " | " # Разделитель для контактной информации
LABEL_LINE_COLOR = (180, 180, 180) # Цвет линии под лейблом (светло-серый)
LABEL_LINE_WIDTH = 0.2 # Толщина линии под лейблом
LABEL_LINE_OFFSET_Y = 0.5 # Небольшой отступ линии от текста лейбла (в мм)
SPACE_AFTER_LINE = 1.5 # Отступ после линии перед текстом значения (в мм)

# --- Font Paths (Keep as is) ---
DEJAVU_FONT_PATH_DIR = "/usr/share/fonts/truetype/dejavu/"
DEJAVU_FONT_REGULAR = os.path.join(DEJAVU_FONT_PATH_DIR, 'DejaVuSans.ttf')
DEJAVU_FONT_BOLD = os.path.join(DEJAVU_FONT_PATH_DIR, 'DejaVuSans-Bold.ttf')

# --- Logging Setup (Keep as is) ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class PDFResumeGenerator:

    def __init__(self):
        global FONT_FAMILY
        self.pdf = FPDF('P', 'mm', 'A4')

        # --- Font Loading Logic (Keep as is) ---
        font_regular_exists = os.path.exists(DEJAVU_FONT_REGULAR)
        font_bold_exists = os.path.exists(DEJAVU_FONT_BOLD)

        if font_regular_exists and font_bold_exists:
            try:
                self.pdf.add_font(FONT_FAMILY, '', DEJAVU_FONT_REGULAR, uni=True)
                self.pdf.add_font(FONT_FAMILY, FONT_STYLE_BOLD, DEJAVU_FONT_BOLD, uni=True)
                log.info(f"Successfully loaded DejaVu fonts from {DEJAVU_FONT_PATH_DIR}")
            except RuntimeError as e:
                log.error(f"Error loading DejaVu font: {e}. Falling back.", exc_info=True)
                FONT_FAMILY = "Arial"
        else:
            if not font_regular_exists: log.warning(f"Font file not found at {DEJAVU_FONT_REGULAR}")
            if not font_bold_exists: log.warning(f"Font file not found at {DEJAVU_FONT_BOLD}")
            log.warning("Falling back to default Arial font.")
            FONT_FAMILY = "Arial"
        # --- End Font Loading ---

        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.set_left_margin(15)
        self.pdf.set_right_margin(15)
        self.line_height = FONT_SIZE_VALUE * LINE_HEIGHT_MULTIPLIER # Базовая высота строки по размеру значения
        log.debug(f"Page width: {self.pdf.w}mm, Left margin: {self.pdf.l_margin}mm, Right margin: {self.pdf.r_margin}mm")
        log.debug(f"Effective page width (epw): {self.pdf.epw}mm")

    def _set_font_normal(self, size=FONT_SIZE_VALUE):
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, size)

    def _set_font_bold(self, size=FONT_SIZE_LABEL):
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, size)

    def _add_text_block(self, text: str, size=FONT_SIZE_VALUE, style=FONT_STYLE_NORMAL):
        try:
            log.debug(f"Adding text block: '{text[:100]}...' at y={self.pdf.get_y()}, x={self.pdf.get_x()}")
            self.pdf.set_font(FONT_FAMILY, style, size)
            available_width = self.pdf.epw
            log.debug(f"Available width for multi_cell: {available_width:.2f}mm")
            self.pdf.multi_cell(0, size * LINE_HEIGHT_MULTIPLIER, text)
            self.pdf.ln(size * LINE_HEIGHT_MULTIPLIER * 0.3)
        except Exception as e:
            log.error(f"Error adding text block: {e}. Text was: '{text}'", exc_info=True)
            raise

    def _extract_header_data(self, resume_data: List[Dict[str, str]]) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
        header_info = {"name": "N/A", "email": "N/A", "phone": "N/A"}
        other_data = []
        found_header_labels = set()

        for item in resume_data:
            label_lower = item.get("label", "").strip().lower()
            value = item.get("value", "")
            found = False

            if label_lower:
                for field_key, keywords in HEADER_FIELDS.items():
                    if label_lower in keywords and label_lower not in found_header_labels:
                        header_info[field_key] = value
                        found_header_labels.add(label_lower)
                        found = True
                        log.debug(f"Found header field '{field_key}' with label '{item.get('label')}'")
                        break

            if not found:
                if item.get("label") and item.get("value"):
                    other_data.append(item)
                else:
                    log.warning(f"Skipping item due to missing label or value: {item}")


        log.info(f"Extracted header: {header_info}")
        other_data = [item for item in other_data if item.get("label") and item.get("value")]
        log.info(f"Remaining data items for main content: {len(other_data)}")
        return header_info, other_data


    def generate(self, resume_data: List[Dict[str, str]]) -> bytes:
        """
        Генерирует PDF резюме из списка label-value пар.
        """
        try:
            log.info("Starting PDF generation with structured data...")
            if not resume_data:
                log.warning("Input resume_data is empty. Generating empty PDF.")
                # Ensure returning bytes even for empty PDF
                pdf_output_raw = self.pdf.output(dest='S')
                if isinstance(pdf_output_raw, bytearray):
                    return bytes(pdf_output_raw)
                elif isinstance(pdf_output_raw, str):
                    return pdf_output_raw.encode('latin-1')
                elif isinstance(pdf_output_raw, bytes):
                    return pdf_output_raw
                else: # Fallback just in case
                     log.error(f"Unexpected type {type(pdf_output_raw)} for empty PDF output.")
                     self._add_text_block("Нет данных для генерации резюме.", style=FONT_STYLE_BOLD)
                     pdf_output_raw = self.pdf.output(dest='S') # Try again after adding text
                     return bytes(pdf_output_raw) if isinstance(pdf_output_raw, bytearray) else pdf_output_raw.encode('latin-1')


            # --- 1. Extract Header Data ---
            header_info, other_data = self._extract_header_data(resume_data)
            name = header_info.get("name", "Имя не указано")
            email = header_info.get("email", "Почта не указана")
            phone = header_info.get("phone", "Телефон не указан")

            # --- 2. Render Header ---
            log.debug(f"Rendering Name: '{name[:50]}...'")
            self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_NAME)
            self.pdf.multi_cell(0, FONT_SIZE_NAME * LINE_HEIGHT_MULTIPLIER * 0.8, name, align='C', new_x="LMARGIN", new_y="NEXT")
            self.pdf.ln(self.line_height * 0.2)

            contact_parts = []
            if email and email != "N/A" and email != "Почта не указана":
                contact_parts.append(f"{email}")
            if phone and phone != "N/A" and phone != "Телефон не указан":
                contact_parts.append(f"{phone}")
            contact_string = HEADER_SEPARATOR.join(contact_parts)

            if contact_string:
                log.debug(f"Rendering Contact: '{contact_string[:100]}...'")
                self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_CONTACT)
                self.pdf.multi_cell(0, FONT_SIZE_CONTACT * LINE_HEIGHT_MULTIPLIER, contact_string, align='C', new_x="LMARGIN", new_y="NEXT")
                self.pdf.ln(self.line_height * 1.5)
            else:
                 log.debug("No contact info (email/phone) found to render.")
                 self.pdf.ln(self.line_height)

            # --- 3. Render Main Content (Label-Value Pairs) ---
            log.debug(f"Rendering {len(other_data)} label-value items...")
            effective_page_width = self.pdf.epw
            log.debug(f"Using effective page width (epw): {effective_page_width:.2f}mm for content.")

            for i, item in enumerate(other_data):
                label = item.get("label", "Нет лейбла").strip()
                value = str(item.get("value", "Нет значения")).strip()

                if not label or not value:
                     log.warning(f"Skipping item {i+1} due to empty label or value after stripping: Label='{label}', Value='{value}'")
                     continue

                log.debug(f"Rendering item {i+1}: Label='{label}', Value='{value[:50]}...'")

                if i > 0:
                    self.pdf.ln(self.line_height * 0.5)

                current_y_before_label = self.pdf.get_y()
                log.debug(f"Before Label '{label}': y={current_y_before_label:.2f}")

                # Render Label (Bold)
                self._set_font_bold(size=FONT_SIZE_LABEL)
                label_height = FONT_SIZE_LABEL * LINE_HEIGHT_MULTIPLIER
                self.pdf.set_x(self.pdf.l_margin)

                if effective_page_width <= 0:
                     log.error(f"EPW is non-positive ({effective_page_width:.2f})! Cannot render label '{label}'.")
                     continue

                self.pdf.multi_cell(effective_page_width, label_height, f"{label}:", new_x="LMARGIN", new_y="NEXT")

                current_y_after_label_text = self.pdf.get_y()
                log.debug(f"After Label Text '{label}': y={current_y_after_label_text:.2f}")

                # --- Add Decorative Line Under Label ---
                line_y = current_y_after_label_text - label_height * 0.3 + LABEL_LINE_OFFSET_Y
                if line_y < current_y_before_label + FONT_SIZE_LABEL * 0.5:
                    line_y = current_y_after_label_text - 1.0
                line_y = max(line_y, self.pdf.t_margin)

                log.debug(f"Drawing decorative line for '{label}' at y={line_y:.2f} (from {self.pdf.l_margin} to {self.pdf.w - self.pdf.r_margin})")
                self.pdf.set_draw_color(*LABEL_LINE_COLOR)
                self.pdf.set_line_width(LABEL_LINE_WIDTH)
                self.pdf.line(self.pdf.l_margin, line_y, self.pdf.w - self.pdf.r_margin, line_y)
                self.pdf.set_draw_color(0, 0, 0)
                self.pdf.set_line_width(0.2) # Reset to fpdf default line width

                self.pdf.ln(SPACE_AFTER_LINE)
                # --- End Decorative Line ---


                current_y_before_value = self.pdf.get_y()
                log.debug(f"After Line & Spacing, Before Value: y={current_y_before_value:.2f}")

                # Render Value (Normal)
                self._set_font_normal(size=FONT_SIZE_VALUE)
                value_height = FONT_SIZE_VALUE * LINE_HEIGHT_MULTIPLIER
                self.pdf.set_x(self.pdf.l_margin)

                log.debug(f"Before Value multi_cell: x={self.pdf.get_x():.2f}, y={self.pdf.get_y():.2f}, width={effective_page_width:.2f}, height={value_height:.2f}")
                if effective_page_width <= 0:
                     log.error(f"EPW is non-positive ({effective_page_width:.2f})! Cannot render value for label '{label}'.")
                     continue

                # Debugging check (keep if useful)
                # if value:
                #     try:
                #         first_char_width = self.pdf.get_string_width(value[0])
                #         log.debug(f"Width of first char '{value[0]}': {first_char_width:.2f}mm")
                #         if first_char_width > effective_page_width:
                #              log.warning(f"First character '{value[0]}' width ({first_char_width:.2f}mm) exceeds effective page width ({effective_page_width:.2f}mm)! This might cause issues.")
                #     except Exception as e:
                #         log.warning(f"Could not get width of first char: {e}")


                self.pdf.multi_cell(effective_page_width, value_height, value, new_x="LMARGIN", new_y="NEXT")

                current_y_after_value = self.pdf.get_y()
                log.debug(f"After Value: y={current_y_after_value:.2f}")

            # --- 4. Output ---
            log.info("PDF generation complete, preparing output.")
            pdf_output_raw = self.pdf.output(dest='S')
            # Log the actual type returned for easier debugging in the future
            log.debug(f"Type returned by self.pdf.output(dest='S'): {type(pdf_output_raw)}")

            pdf_output_bytes = None # Initialize
            if isinstance(pdf_output_raw, bytes):
                pdf_output_bytes = pdf_output_raw
                log.debug("self.pdf.output(dest='S') returned bytes.")
            # ***** ADDED CHECK FOR BYTEARRAY *****
            elif isinstance(pdf_output_raw, bytearray):
                pdf_output_bytes = bytes(pdf_output_raw) # Convert bytearray to bytes
                log.debug("self.pdf.output(dest='S') returned bytearray, converted to bytes.")
            # ***** END ADDED CHECK *****
            elif isinstance(pdf_output_raw, str):
                log.warning("self.pdf.output(dest='S') returned str, encoding to latin-1.")
                try:
                    pdf_output_bytes = pdf_output_raw.encode('latin-1')
                except Exception as enc_err:
                    log.error(f"Failed to encode PDF output string to latin-1: {enc_err}", exc_info=True)
                    # Raising a more specific error might be better, but TypeError is okay here
                    raise TypeError("Failed to get PDF content as bytes") from enc_err
            else:
                 # This block now correctly handles unexpected types that are NOT bytes, bytearray, or str
                 error_msg = f"FPDF output(dest='S') returned unexpected type: {type(pdf_output_raw)}. Expected bytes, bytearray, or str."
                 log.error(error_msg)
                 raise TypeError(error_msg)


            # Final check before returning
            if not isinstance(pdf_output_bytes, bytes):
                 # This should technically not be reachable if the logic above is correct, but serves as a safeguard
                 error_msg = f"PDF generation result is not bytes after processing. Got {type(pdf_output_bytes)}."
                 log.error(error_msg)
                 raise TypeError(error_msg)

            log.info(f"PDF generated successfully (type: bytes), size: {len(pdf_output_bytes)} bytes.")
            return pdf_output_bytes

        except Exception as e:
             log.error(f"Failed to generate PDF: {e}", exc_info=True)
             raise


# --- Function to call from router (обновленная) ---
def create_resume_pdf(resume_data: List[Dict[str, str]]) -> bytes:
    """
    Creates a resume PDF from a list of label-value dictionaries.

    Args:
        resume_data: List of dictionaries, each with "label" and "value" keys.

    Returns:
        bytes: The generated PDF content.

    Raises:
        Exception: Any exception during PDF generation.
    """
    log.info("Received request to create PDF resume from structured data.")
    if not isinstance(resume_data, list):
        log.error(f"Invalid input type for create_resume_pdf: expected list, got {type(resume_data)}")
        raise TypeError("Input data must be a list of dictionaries.")

    # Basic validation of list items (optional but good practice)
    # for i, item in enumerate(resume_data):
    #     if not isinstance(item, dict) or "label" not in item or "value" not in item:
    #          log.error(f"Invalid item format at index {i}: {item}. Expected dict with 'label' and 'value'.")
    #          # Decide whether to raise error or filter/skip
    #          # raise ValueError(f"Invalid item format at index {i}")
    #          log.warning(f"Skipping invalid item at index {i}.")

    try:
        generator = PDFResumeGenerator()
        pdf_content = generator.generate(resume_data)

        # The generate function now ensures it returns bytes or raises an error
        # So this check might seem redundant, but it's a good final assertion
        if not isinstance(pdf_content, bytes):
            error_msg = f"CRITICAL Error: PDF generator returned non-bytes type: {type(pdf_content)}."
            log.error(error_msg)
            # Attempt recovery only if absolutely necessary and possible (unlikely here)
            raise TypeError(error_msg)

        log.info("PDF content generated and validated (type: bytes).")
        return pdf_content

    except Exception as e:
         log.error(f"Error in create_resume_pdf function: {e}", exc_info=True)
         raise # Re-raise for FastAPI/caller to handle
