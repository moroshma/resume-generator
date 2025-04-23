# ai_service/services/pdf_generator.py
import os
from fpdf import FPDF
from typing import Dict, List, Any
import datetime
import re # Import regex for potential key matching
import logging

# --- Constants ---
FONT_FAMILY = "DejaVu"
FONT_STYLE_NORMAL = ""
FONT_STYLE_BOLD = "B"
FONT_SIZE_NAME = 18
FONT_SIZE_CONTACT = 10
FONT_SIZE_HEADING = 12
FONT_SIZE_SUBHEADING = 11
FONT_SIZE_NORMAL = 10
LINE_HEIGHT_MULTIPLIER = 1.4 # Slightly adjusted line height

# --- Font Paths (Keep as is) ---
DEJAVU_FONT_PATH_DIR = "/usr/share/fonts/truetype/dejavu/"
DEJAVU_FONT_REGULAR = os.path.join(DEJAVU_FONT_PATH_DIR, 'DejaVuSans.ttf')
DEJAVU_FONT_BOLD = os.path.join(DEJAVU_FONT_PATH_DIR, 'DejaVuSans-Bold.ttf')

# --- Placeholder Texts ---
PLACEHOLDER_TEXT = {
    "name": "YOUR FULL NAME",
    "contact": "Your Address | Your Phone | Your Email | Your LinkedIn/Portfolio (Optional)",
    "summary": "Write a brief professional summary highlighting your key skills, experience, and career goals. Tailor this to the job you are applying for.",
    "experience": "- **[Job Title]** at [Company Name] ([Start Date] - [End Date])\n  - [Responsibility or achievement 1]\n  - [Responsibility or achievement 2]\n  - [Add more relevant details or projects]",
    "education": "- **[Degree Name]** - [Major/Field of Study]\n  [Institution Name], [City, State] ([Year Graduated])\n  - [Optional: Relevant coursework, honors, GPA if high]",
    "soft_skills": "Communication, Teamwork, Problem-Solving, Adaptability, Time Management", # Example soft skills
}


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
                log.info(f"Successfully loaded DejaVu fonts from {DEJAVU_FONT_PATH_DIR}") # Используем log.info
            except RuntimeError as e:
                log.error(f"Error loading DejaVu font: {e}. Falling back.", exc_info=True) # Используем log.error с traceback
                FONT_FAMILY = "Arial"
        else:
            if not font_regular_exists: log.warning(f"Font file not found at {DEJAVU_FONT_REGULAR}") # log.warning
            if not font_bold_exists: log.warning(f"Font file not found at {DEJAVU_FONT_BOLD}") # log.warning
            log.warning("Falling back to default Arial font.")
            FONT_FAMILY = "Arial"
        # --- End Font Loading ---

        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15) # Нижний отступ для автопереноса
        self.pdf.set_left_margin(15)
        self.pdf.set_right_margin(15)
        self.line_height = FONT_SIZE_NORMAL * LINE_HEIGHT_MULTIPLIER
        # Добавим отладочную информацию о размерах
        log.debug(f"Page width: {self.pdf.w}mm, Left margin: {self.pdf.l_margin}mm, Right margin: {self.pdf.r_margin}mm")
        log.debug(f"Effective page width (epw): {self.pdf.epw}mm")


    def _set_font_normal(self):
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_NORMAL)

    def _set_font_bold(self):
        self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_NORMAL)

    def _add_section_heading(self, title: str):
        try:
            log.debug(f"Adding section heading: '{title[:50]}...' at y={self.pdf.get_y()}")
            self.pdf.ln(self.line_height * 0.7)
            self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_HEADING)
            # Проверим ширину заголовка перед отрисовкой
            title_width = self.pdf.get_string_width(title.upper())
            available_width = self.pdf.epw # Effective Page Width
            log.debug(f"Section heading width: {title_width:.2f}mm, Available width: {available_width:.2f}mm")
            if title_width > available_width:
                 log.warning(f"Section heading '{title.upper()}' might be too wide!")
            self.pdf.cell(0, self.line_height * 1.2, title.upper(), border='B', ln=1, align='L')
            self.pdf.ln(self.line_height * 0.5)
            self._set_font_normal()
        except Exception as e:
            log.error(f"Error adding section heading '{title}': {e}", exc_info=True)
            raise # Перевыбрасываем исключение, чтобы остановить генерацию

    def _add_text_block(self, text: str):
        try:
            log.debug(f"Adding text block: '{text[:100]}...' at y={self.pdf.get_y()}, x={self.pdf.get_x()}")
            available_width = self.pdf.w - self.pdf.r_margin - self.pdf.get_x()
            log.debug(f"Available width for multi_cell: {available_width:.2f}mm")
            # Проверим самое длинное слово на всякий случай
            longest_word = max(re.split(r'\s+', text), key=len) if text else ""
            if longest_word:
                word_width = self.pdf.get_string_width(longest_word)
                log.debug(f"Longest word ('{longest_word[:30]}...') width: {word_width:.2f}mm")
                if word_width > self.pdf.epw:
                    log.warning(f"Potentially problematic long word found! Width {word_width:.2f}mm > Effective Page Width {self.pdf.epw:.2f}mm")

            self.pdf.multi_cell(0, self.line_height, text)
            self.pdf.ln(self.line_height * 0.3)
        except Exception as e:
            # Если ошибка именно здесь, логируем текст
            log.error(f"Error adding text block: {e}. Text was: '{text}'", exc_info=True)
            raise

    def _add_list_items(self, items: List[str]):
        if not items:
            self._add_text_block("N/A")
            return
        for i, item in enumerate(items):
            try:
                log.debug(f"Adding list item {i+1}: '{item[:100]}...' at y={self.pdf.get_y()}, x={self.pdf.get_x()}")
                text_to_render = f"• {item}"

                # Рассчитываем доступную ширину явно
                available_width = self.pdf.epw # epw = w - l_margin - r_margin
                log.debug(f"Using explicit width for multi_cell: {available_width:.2f}mm for item '{item}'")

                if available_width <= 0:
                    log.error(f"CRITICAL: Calculated available width ({available_width:.2f}mm) is not positive before rendering '{item}'!")
                    raise ValueError(f"Invalid available width calculated: {available_width}")

                # Используем рассчитанную ширину
                self.pdf.multi_cell(available_width, self.line_height, text_to_render)

                # Опционально: добавить небольшой отступ после каждого элемента списка
                # self.pdf.ln(self.line_height * 0.1)

            except Exception as e:
                 log.error(f"Error adding list item: {e}. Item was: '{item}'", exc_info=True)
                 raise
        # Этот ln() теперь либо не нужен, либо управляет отступом ПОСЛЕ всего списка
        self.pdf.ln(self.line_height * 0.3)


    def _find_answer(self, user_answers: Dict[str, str], keywords: List[str]) -> str | None:
        """
        Ищет в словаре user_answers вопрос (ключ), содержащий любое из
        переданных ключевых слов (без учета регистра).

        Args:
            user_answers: Словарь пар вопрос-ответ.
            keywords: Список строк для поиска в вопросах (ключах).

        Returns:
            Строку ответа, соответствующую первому найденному вопросу,
            или None, если ни один вопрос не соответствует ни одному ключевому слову.
        """
        if not user_answers or not keywords:
            log.debug("_find_answer: Получены пустые ответы или ключевые слова.")
            return None # Обработка крайних случаев

        log.debug(f"Поиск ответа по ключевым словам: {keywords}")

        # Перебираем каждый вопрос и ответ в словаре
        for question, answer in user_answers.items():
            # Приводим вопрос к нижнему регистру для сравнения без учета регистра
            question_lower = question.lower()

            # Проверяем, содержит ли вопрос в нижнем регистре
            # хотя бы одно из ключевых слов (тоже в нижнем регистре)
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Используем 'in' для проверки наличия подстроки.
                # Это позволяет находить "name" в "What is your full name?"
                if keyword_lower in question_lower:
                    log.debug(f"Найдено совпадение: ключ '{keyword}' в вопросе '{question}'. Возвращаем ответ.")
                    # Если найдено совпадение, возвращаем соответствующий ответ
                    return answer

        # Если цикл завершился, и мы ничего не вернули, значит совпадений не было
        log.debug(f"Не найдено ни одного вопроса, соответствующего ключевым словам: {keywords}")
        return None

    def generate(self, user_answers: Dict[str, str], generated_skills: List[str]) -> bytes:
        """
        Generates a more complete-looking resume PDF. (Includes debug logging)
        """
        try:
            log.info("Starting PDF generation...")
            # --- 1. Header: Name and Contact Info ---
            name = self._find_answer(user_answers, ["name", "full name"]) or PLACEHOLDER_TEXT["name"]
            contact = self._find_answer(user_answers, ["contact", "email", "phone", "address", "linkedin"]) or PLACEHOLDER_TEXT["contact"]

            log.debug(f"Adding Name: '{name[:50]}...'")
            self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_NAME)
            self.pdf.cell(0, self.line_height * 1.5, name, ln=1, align='C')

            log.debug(f"Adding Contact: '{contact[:100]}...'")
            self.pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_CONTACT)
            self.pdf.cell(0, self.line_height * 0.8, contact, ln=1, align='C')
            self.pdf.ln(self.line_height)

            # --- 2. Summary/Objective ---
            self._add_section_heading("Summary")
            summary_text = self._find_answer(user_answers, ["summary", "objective", "profile", "about yourself"]) or PLACEHOLDER_TEXT["summary"]
            self._set_font_normal()
            self._add_text_block(summary_text)

            # --- 3. Work Experience ---
            self._add_section_heading("Experience")
            experience_found = False
            # ... (логика поиска опыта) ...
            for q, a in user_answers.items():
                if re.search(r'\b(experience|role|job|project|worked on|responsibilit(y|ies))\b', q, re.IGNORECASE) and \
                   not re.search(r'\b(summary|objective|profile|about yourself|skill|education|degree)\b', q, re.IGNORECASE):
                    log.debug(f"Adding experience block for question: '{q[:50]}...'")
                    self._set_font_bold()
                    q_cleaned = q.replace("Describe your ", "").replace("Tell me about ","").replace("?","")
                    # Используем multi_cell для заголовка вопроса, т.к. он может быть длинным
                    self._add_text_block(f"Regarding: {q_cleaned}") # Заменили cell на text_block
                    self._set_font_normal()
                    self._add_text_block(f"- {a}") # Используем text_block для ответа
                    experience_found = True

            if not experience_found:
                log.debug("No specific experience found, adding placeholder.")
                self._set_font_normal()
                self._add_text_block(PLACEHOLDER_TEXT["experience"])

            # --- 4. Education ---
            self._add_section_heading("Education")
            education_text = self._find_answer(user_answers, ["education", "degree", "university", "college", "studied"])
            self._set_font_normal()
            if education_text:
                 log.debug(f"Adding education block: '{education_text[:100]}...'")
                 self._add_text_block(f"- {education_text}")
            else:
                 log.debug("No specific education found, adding placeholder.")
                 self._add_text_block(PLACEHOLDER_TEXT["education"])


            # --- 5. Skills ---
            self._add_section_heading("Skills")

            if generated_skills:
                 log.debug("Adding generated hard skills.")
                 self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_SUBHEADING)
                 # Используем multi_cell для заголовка подраздела на всякий случай
                 self.pdf.multi_cell(0, self.line_height * 1.1, "Technical / Hard Skills:")
                 self.pdf.ln(self.line_height * 0.1) # Небольшой отступ после заголовка подраздела
                 self._set_font_normal()
                 self._add_list_items(generated_skills)
            else:
                 log.debug("No generated skills, adding placeholder.")
                 self._set_font_normal()
                 self._add_text_block("[List relevant technical skills here, e.g., Programming Languages, Software, Tools]")

            self.pdf.ln(self.line_height * 0.2)

            soft_skills_text = self._find_answer(user_answers, ["soft skill", "interpersonal", "communication", "teamwork"])
            log.debug("Adding soft skills section.")
            self.pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_SUBHEADING)
             # Используем multi_cell для заголовка подраздела
            self.pdf.multi_cell(0, self.line_height * 1.1, "Soft Skills:")
            self.pdf.ln(self.line_height * 0.1)
            self._set_font_normal()
            if soft_skills_text:
                log.debug(f"Adding found soft skills: '{soft_skills_text[:100]}...'")
                self._add_text_block(soft_skills_text)
            else:
                log.debug("No specific soft skills found, adding placeholder.")
                self._add_text_block(PLACEHOLDER_TEXT["soft_skills"])

            # --- Output ---
            log.info("PDF generation complete, preparing output.")
            pdf_output_data = self.pdf.output()
            log.debug(f"Type returned by self.pdf.output(): {type(pdf_output_data)}") # Добавим лог типа

            pdf_bytes_final: bytes # Объявим тип для ясности

            if isinstance(pdf_output_data, bytearray):
                # Если вернулся bytearray, преобразуем его в bytes
                log.warning("FPDF output() returned bytearray. Converting to bytes.")
                pdf_bytes_final = bytes(pdf_output_data)
            elif isinstance(pdf_output_data, bytes):
                # Если вернулся ожидаемый bytes, просто используем его
                pdf_bytes_final = pdf_output_data
            elif isinstance(pdf_output_data, str):
                # Обработка строки (менее вероятно с fpdf2, но оставим на всякий случай)
                log.critical(f"FPDF output() returned str, expected bytes or bytearray!")
                try:
                    log.warning("Attempting to encode problematic string output using latin-1 (may break non-latin chars)...")
                    pdf_bytes_final = pdf_output_data.encode('latin-1')
                except Exception as e:
                     log.error(f"Failed to encode string output from FPDF: {e}", exc_info=True)
                     raise TypeError(f"FPDF output was str, expected bytes/bytearray, and encoding failed.")
            else:
                # Если вернулся какой-то совершенно другой тип
                error_msg = f"FPDF output returned unexpected type: {type(pdf_output_data)}. Expected bytes or bytearray."
                log.error(error_msg)
                raise TypeError(error_msg)

            # Теперь pdf_bytes_final гарантированно имеет тип bytes
            log.info(f"PDF generated successfully (type: {type(pdf_bytes_final)}), size: {len(pdf_bytes_final)} bytes.")
            return pdf_bytes_final

        except Exception as e:
             # Логируем любую ошибку во время генерации PDF
             log.error(f"Failed to generate PDF: {e}", exc_info=True)
             # Перевыбрасываем ошибку, чтобы внешний обработчик вернул 500
             raise


# --- Function to call from router (обновленная) ---
def create_resume_pdf(user_answers: Dict[str, str], generated_skills: List[str]) -> bytes:
    """
    Creates a standard-looking resume PDF using user answers and generated skills.
    Includes detailed logging for debugging generation issues.

    Args:
        user_answers: Dictionary of question-answer pairs.
        generated_skills: List of hard skills generated by the AI.

    Returns:
        bytes: The generated PDF content.

    Raises:
        Exception: Any exception during PDF generation will be propagated.
                   TypeError if the generator returns an unexpected type.
    """
    log.info("Received request to create PDF resume.") # Используем логгер
    try:
        generator = PDFResumeGenerator()
        pdf_content = generator.generate(user_answers, generated_skills)

        # Строгая проверка типа остается важной
        log.debug(f"Type returned by generator.generate(): {type(pdf_content)}")

        if not isinstance(pdf_content, bytes):
            error_msg = f"CRITICAL Error: PDF generator was expected to return bytes, but returned {type(pdf_content)}."
            log.error(error_msg)
            raise TypeError(error_msg) # Важно остановить процесс здесь

        log.info("PDF content generated and validated (type: bytes).")
        return pdf_content

    except Exception as e:
         # Логируем ошибку на верхнем уровне и позволяем фреймворку вернуть 500
         # Ошибка уже должна быть залогирована внутри generate() с большим контекстом
         log.error(f"Error in create_resume_pdf function: {e}", exc_info=True)
         # Перевыбрасываем, чтобы FastAPI/Starlette обработал и вернул 500
         raise # Не возвращайте здесь пустые байты или что-то еще!
