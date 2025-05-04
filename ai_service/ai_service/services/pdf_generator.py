# ai_service/services/pdf_generator.py
import os
from fpdf import FPDF
from typing import Dict, List, Any, Tuple # Добавим Tuple
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

    # Удаляем _add_section_heading, т.к. секции теперь не нужны в старом виде
    # def _add_section_heading(self, title: str): ...

    # Оставляем _add_text_block, но, возможно, он будет меньше использоваться
    def _add_text_block(self, text: str, size=FONT_SIZE_VALUE, style=FONT_STYLE_NORMAL):
        try:
            log.debug(f"Adding text block: '{text[:100]}...' at y={self.pdf.get_y()}, x={self.pdf.get_x()}")
            self.pdf.set_font(FONT_FAMILY, style, size)
            available_width = self.pdf.epw # Используем эффективную ширину страницы
            log.debug(f"Available width for multi_cell: {available_width:.2f}mm")
            self.pdf.multi_cell(0, size * LINE_HEIGHT_MULTIPLIER, text) # Используем размер шрифта для высоты строки
            self.pdf.ln(size * LINE_HEIGHT_MULTIPLIER * 0.3) # Небольшой отступ после блока
        except Exception as e:
            log.error(f"Error adding text block: {e}. Text was: '{text}'", exc_info=True)
            raise

    # _add_list_items тоже не нужен в старом виде
    # def _add_list_items(self, items: List[str]): ...

    # Удаляем _find_answer, он больше не нужен
    # def _find_answer(self, user_answers: Dict[str, str], keywords: List[str]) -> str | None: ...


    def _extract_header_data(self, resume_data: List[Dict[str, str]]) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
        """
        Извлекает данные для шапки (ФИО, Почта, Телефон) из общего списка
        и возвращает их отдельно от остальных данных.
        """
        header_info = {"name": "N/A", "email": "N/A", "phone": "N/A"}
        other_data = []
        found_header_labels = set() # Чтобы не добавлять дубликаты по разным ключевым словам

        for item in resume_data:
            label_lower = item.get("label", "").lower()
            value = item.get("value", "")
            found = False

            # Проверяем, относится ли лейбл к полям шапки
            for field_key, keywords in HEADER_FIELDS.items():
                if label_lower in keywords and label_lower not in found_header_labels:
                    header_info[field_key] = value
                    found_header_labels.add(label_lower) # Помечаем, что этот лейбл обработан
                    found = True
                    log.debug(f"Found header field '{field_key}' with label '{item.get('label')}'")
                    break # Переходим к следующему item

            # Если это не поле шапки, добавляем в список остальных данных
            if not found:
                other_data.append(item)

        log.info(f"Extracted header: {header_info}")
        return header_info, other_data


    def generate(self, resume_data: List[Dict[str, str]]) -> bytes:
        """
        Генерирует PDF резюме из списка label-value пар.
        """
        try:
            log.info("Starting PDF generation with structured data...")
            if not resume_data:
                log.warning("Input resume_data is empty. Generating empty PDF.")
                self._add_text_block("Нет данных для генерации резюме.", style=FONT_STYLE_BOLD)
                # Вывод пустого PDF, чтобы не было ошибки
                return self.pdf.output()

            # --- 1. Extract Header Data ---
            header_info, other_data = self._extract_header_data(resume_data)
            name = header_info.get("name", "Имя не указано")
            email = header_info.get("email", "Почта не указана")
            phone = header_info.get("phone", "Телефон не указан")

            # --- 2. Render Header ---
            log.debug(f"Rendering Name: '{name[:50]}...'")
            self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_NAME)
            self.pdf.cell(0, FONT_SIZE_NAME * LINE_HEIGHT_MULTIPLIER * 0.8, name, ln=1, align='C') # Уменьшил высоту строки для имени
            self.pdf.ln(self.line_height * 0.2) # Небольшой отступ после имени

            # Собираем контактную строку
            contact_parts = []
            if email and email != "N/A" and email != "Почта не указана":
                contact_parts.append(f"{email}")
            if phone and phone != "N/A" and phone != "Телефон не указан":
                contact_parts.append(f"{phone}")
            contact_string = HEADER_SEPARATOR.join(contact_parts)

            if contact_string:
                log.debug(f"Rendering Contact: '{contact_string[:100]}...'")
                self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_CONTACT)
                self.pdf.cell(0, FONT_SIZE_CONTACT * LINE_HEIGHT_MULTIPLIER, contact_string, ln=1, align='C')
                self.pdf.ln(self.line_height * 1.5) # Увеличиваем отступ после контактов
            else:
                 log.debug("No contact info (email/phone) found to render.")
                 self.pdf.ln(self.line_height) # Отступ даже если контактов нет

            # --- 3. Render Main Content (Label-Value Pairs) ---
            log.debug(f"Rendering {len(other_data)} label-value items...")
            effective_page_width = self.pdf.epw # Calculate once
            log.debug(f"Using effective page width (epw): {effective_page_width:.2f}mm for content.")

            for i, item in enumerate(other_data):
                label = item.get("label", "Нет лейбла")
                value = str(item.get("value", "Нет значения")) # Ensure value is a string

                log.debug(f"Rendering item {i+1}: Label='{label}', Value='{value[:50]}...'")

                # Add spacing before the item
                if i > 0:
                    self.pdf.ln(self.line_height * 0.6)

                current_y_before_label = self.pdf.get_y()
                log.debug(f"Before Label '{label}': y={current_y_before_label:.2f}")

                # Render Label (Bold)
                self._set_font_bold(size=FONT_SIZE_LABEL)
                label_height = FONT_SIZE_LABEL * LINE_HEIGHT_MULTIPLIER
                self.pdf.set_x(self.pdf.l_margin) # Ensure starting at left margin

                # Use explicit width (epw) for label multi_cell
                if effective_page_width <= 0:
                     log.error(f"EPW is non-positive ({effective_page_width:.2f})! Cannot render label '{label}'.")
                     continue # Skip this item
                self.pdf.multi_cell(effective_page_width, label_height, f"{label}:", new_x="LMARGIN", new_y="NEXT")
                # No need for extra ln after multi_cell with new_y="NEXT"

                current_y_after_label = self.pdf.get_y()
                log.debug(f"After Label '{label}': y={current_y_after_label:.2f}")


                # Render Value (Normal)
                self._set_font_normal(size=FONT_SIZE_VALUE)
                value_height = FONT_SIZE_VALUE * LINE_HEIGHT_MULTIPLIER
                self.pdf.set_x(self.pdf.l_margin) # Ensure starting at left margin

                # Use explicit width (epw) instead of 0 for value multi_cell
                log.debug(f"Before Value multi_cell: x={self.pdf.get_x():.2f}, y={self.pdf.get_y():.2f}, width={effective_page_width:.2f}, height={value_height:.2f}")
                if effective_page_width <= 0:
                     log.error(f"EPW is non-positive ({effective_page_width:.2f})! Cannot render value for label '{label}'.")
                     continue # Skip this item

                # Add a small check for the first character width if possible (for debugging)
                if value:
                    try:
                        first_char_width = self.pdf.get_string_width(value[0])
                        log.debug(f"Width of first char '{value[0]}': {first_char_width:.2f}mm")
                        if first_char_width > effective_page_width:
                             log.warning(f"First character '{value[0]}' width ({first_char_width:.2f}mm) exceeds effective page width ({effective_page_width:.2f}mm)! This might cause issues.")
                    except Exception as e:
                        log.warning(f"Could not get width of first char: {e}")


                # Use multi_cell with explicit width
                self.pdf.multi_cell(effective_page_width, value_height, value, new_x="LMARGIN", new_y="NEXT")
                # No need for extra ln after multi_cell with new_y="NEXT"

                current_y_after_value = self.pdf.get_y()
                log.debug(f"After Value: y={current_y_after_value:.2f}")

            # --- 4. Output ---
            log.info("PDF generation complete, preparing output.")
            # Get the raw output from fpdf2 (likely bytearray or bytes)
            pdf_output_raw = self.pdf.output(dest='S')
            log.debug(f"Type returned by self.pdf.output(dest='S'): {type(pdf_output_raw)}")

            # Ensure the final result is specifically a 'bytes' object
            if isinstance(pdf_output_raw, bytearray):
                pdf_output_bytes = bytes(pdf_output_raw)
                log.debug("Converted bytearray to bytes.")
            elif isinstance(pdf_output_raw, bytes):
                 pdf_output_bytes = pdf_output_raw # Already the desired type
                 log.debug("Output was already bytes.")
            else:
                 # Handle unexpected type if necessary, though unlikely now
                 error_msg = f"FPDF output(dest='S') returned unexpected type: {type(pdf_output_raw)}. Expected bytes or bytearray."
                 log.error(error_msg)
                 raise TypeError(error_msg)

            if not isinstance(pdf_output_bytes, bytes):
                 error_msg = f"FPDF output encoding failed. Expected bytes, got {type(pdf_output_bytes)}."
                 log.error(error_msg)
                 raise TypeError(error_msg)

            log.info(f"PDF generated successfully (type: bytes), size: {len(pdf_output_bytes)} bytes.")
            return pdf_output_bytes

        except Exception as e:
             log.error(f"Failed to generate PDF: {e}", exc_info=True)
             raise


# --- Function to call from router (обновленная) ---
# Принимает List[Dict[str, str]], который должен быть подготовлен в роутере
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
    # Можно добавить проверку, что элементы списка - это dict с нужными ключами, если нужно

    try:
        generator = PDFResumeGenerator()
        pdf_content = generator.generate(resume_data)

        if not isinstance(pdf_content, bytes):
            error_msg = f"CRITICAL Error: PDF generator was expected to return bytes, but returned {type(pdf_content)}."
            log.error(error_msg)
            raise TypeError(error_msg)

        log.info("PDF content generated and validated (type: bytes).")
        return pdf_content

    except Exception as e:
         log.error(f"Error in create_resume_pdf function: {e}", exc_info=True)
         raise # Перевыбрасываем для обработки FastAPI
