import os
import re
import sys
import pymupdf


INPUT_PDF = "input.pdf"
OUTPUT_TXT = "extracted_practicals.txt"


# ============================================================
# PRACTICAL START
# ============================================================

PRACTICAL_RE = re.compile(
    r"^\s*Practical\s+No\.?\s*(\d+)\s*$",
    re.IGNORECASE
)


# ============================================================
# SECTION MARKERS
# ============================================================

I_ONLY_RE = re.compile(
    r"^\s*I\s*\.\s*$",
    re.IGNORECASE
)

PRACTICAL_SIGNIFICANCE_RE = re.compile(
    r"^\s*Practical\s+Significance\s*$",
    re.IGNORECASE
)

EXERCISE_FULL_RE = re.compile(
    r"^\s*VIII\s*\.\s*Exercise\s*$",
    re.IGNORECASE
)

EXERCISE_ONLY_RE = re.compile(
    r"^\s*Exercise\s*$",
    re.IGNORECASE
)

VIII_ONLY_RE = re.compile(
    r"^\s*VIII\s*\.\s*$",
    re.IGNORECASE
)

RELATED_FULL_RE = re.compile(
    r"^\s*IX\s*\.\s*Practical\s+related\s+questions?.*$",
    re.IGNORECASE
)

RELATED_ONLY_RE = re.compile(
    r"^\s*Practical\s+related\s+questions?.*$",
    re.IGNORECASE
)

IX_ONLY_RE = re.compile(
    r"^\s*IX\s*\.\s*$",
    re.IGNORECASE
)

REFERENCES_RE = re.compile(
    r"^\s*X\s*\.?\s*References\s*/?\s*"
    r"Suggestions?\s+for\s+further\s+Reading.*$",
    re.IGNORECASE
)

ASSESSMENT_RE = re.compile(
    r"^\s*XI\s*\.?\s*Assessment\s+Scheme.*$",
    re.IGNORECASE
)


# ============================================================
# QUESTION MARKERS
#
# IMPORTANT:
# The raw PDF uses BOTH:
#
#   1. Question
#   2) Question
#
# ============================================================

QUESTION_RE = re.compile(
    r"^\s*(\d+)\s*[\.)]\s*(.*)$"
)

BULLET_RE = re.compile(
    r"^\s*[•]\s*(.*)$"
)

LETTER_SUBPART_RE = re.compile(
    r"^\s*([a-hA-H])\s*[\.)]\s*(.*)$"
)

ROMAN_SUBPART_RE = re.compile(
    r"^\s*([ivxlcdmIVXLCDM]+)\s*[\.)]\s*(.*)$"
)


# ============================================================
# NOTE
# ============================================================

NOTE_RE = re.compile(
    r"^\s*Note\s*:",
    re.IGNORECASE
)


# ============================================================
# PAGE HEADER/F0OTER DETECTION
# ============================================================

def normalized_letters(text):
    """
    Keep only alphabetic characters and lowercase them.

    Used to detect header variants such as:

        STATISTICAL MODELLING FOR MACHINE LEARNING
        STATISTICAL: MODELLING FOR MACHINE LEARNING
        STATISTICAL  MODELLING...
    """

    return re.sub(
        r"[^a-z]",
        "",
        text.lower()
    )


HEADER_CANONICAL = (
    "datastructureusingpython"
)


def is_page_header(line):

    compact = normalized_letters(line)

    return compact == HEADER_CANONICAL


def is_course_code(line):

    compact = re.sub(
        r"[^a-z0-9]",
        "",
        line.lower()
    )

    return compact in {
        "coursecode313306",
        "courscode313306"
    }


def is_scheme(line):

    compact = re.sub(
        r"[^a-z0-9]",
        "",
        line.lower()
    )

    return compact in {
        "msbtekkscheme",
        "msbtekkscheme",
        "msbtekkscheme"
    }


# ============================================================
# ANSWER SPACE
# ============================================================

def is_answer_marker(line):

    compact = re.sub(
        r"[^a-z]",
        "",
        line.lower()
    )

    return compact in {
        "spaceforanswers",
        "spaceofanswers"
    }


def is_blank_instruction(line):

    compact = re.sub(
        r"[^a-z]",
        "",
        line.lower()
    )

    target = (
        "useblankspaceforanswersorattachmorepagesifneeded"
    )

    return compact == target


def is_dot_line(line):

    return bool(
        re.fullmatch(
            r"\s*\.{10,}\s*",
            line
        )
    )


# ============================================================
# PAGE CLEANING
# ============================================================

def clean_page(page_text):

    raw_lines = page_text.splitlines()

    cleaned = []

    for line in raw_lines:

        line = line.strip()

        if not line:
            continue

        if is_page_header(line):
            continue

        if is_course_code(line):
            continue

        if is_scheme(line):
            continue

        if is_answer_marker(line):
            continue

        if is_blank_instruction(line):
            continue

        if is_dot_line(line):
            continue

        # Page numbers:
        # We remove standalone numerical lines because in this
        # document they are page numbers / form artifacts.
        if re.fullmatch(
            r"\s*\d+\s*",
            line
        ):

            continue

        cleaned.append(
            re.sub(
                r"\s+",
                " ",
                line
            ).strip()
        )

    return cleaned


# ============================================================
# PDF -> PAGES
# ============================================================

def extract_pages(pdf_path):

    document = pymupdf.open(
        pdf_path
    )

    pages = []

    for page_number, page in enumerate(
        document,
        start=1
    ):

        text = page.get_text(
            "text",
            sort=True
        )

        lines = clean_page(
            text
        )

        pages.append(
            {
                "page": page_number,
                "lines": lines
            }
        )

    document.close()

    return pages


# ============================================================
# MAKE DOCUMENT WITH PAGE BOUNDARIES
# ============================================================

def flatten_pages(pages):

    result = []

    for page in pages:

        result.extend(
            page["lines"]
        )

        result.append(
            "<PAGE_BREAK>"
        )

    return result


# ============================================================
# FIND PRACTICALS
# ============================================================

def find_practicals(lines):

    starts = []

    for i, line in enumerate(lines):

        match = PRACTICAL_RE.match(
            line
        )

        if match:

            starts.append(
                {
                    "index": i,
                    "number": int(
                        match.group(1)
                    )
                }
            )

    practicals = []

    for i, start in enumerate(starts):

        if i + 1 < len(starts):

            end = starts[
                i + 1
            ]["index"]

        else:

            end = len(lines)

        practicals.append(
            {
                "number": start["number"],
                "start": start["index"],
                "end": end
            }
        )

    return practicals


# ============================================================
# FIND PRACTICAL SIGNIFICANCE
# ============================================================

def find_significance(
    lines,
    start,
    end
):

    for i in range(
        start + 1,
        end
    ):

        line = lines[i]

        if I_ONLY_RE.match(line):

            # I.
            # Practical Significance
            if (
                i + 1 < end
                and PRACTICAL_SIGNIFICANCE_RE.match(
                    lines[i + 1]
                )
            ):

                return i

        # I. Practical Significance
        if re.match(
            r"^\s*I\s*\.\s*Practical\s+Significance\s*$",
            line,
            re.IGNORECASE
        ):

            return i

        # Practical Significance alone
        if PRACTICAL_SIGNIFICANCE_RE.match(
            line
        ):

            return i

    return None


# ============================================================
# TITLE
# ============================================================

def extract_title(
    lines,
    start,
    significance,
    number
):

    title_lines = []

    for i in range(
        start + 1,
        significance
    ):

        line = lines[i]

        if line == "<PAGE_BREAK>":
            continue

        title_lines.append(
            line
        )

    title = " ".join(
        title_lines
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    return (
        f"Practical {number}: {title}"
        if title
        else f"Practical {number}"
    )


# ============================================================
# FIND EXERCISE
# ============================================================

def find_exercise(
    lines,
    start,
    end
):

    for i in range(
        start,
        end
    ):

        line = lines[i]

        # VIII. Exercise
        if EXERCISE_FULL_RE.match(
            line
        ):

            return i

        # VIII.
        # Exercise
        if VIII_ONLY_RE.match(
            line
        ):

            if (
                i + 1 < end
                and EXERCISE_ONLY_RE.match(
                    lines[i + 1]
                )
            ):

                return i + 1

        # Exercise alone
        if EXERCISE_ONLY_RE.match(
            line
        ):

            return i

    return None


# ============================================================
# FIND PRACTICAL RELATED QUESTIONS
# ============================================================

def find_related(
    lines,
    start,
    end
):

    for i in range(
        start,
        end
    ):

        line = lines[i]

        # IX. Practical related questions ...
        if RELATED_FULL_RE.match(
            line
        ):

            return i

        # IX.
        # Practical related questions ...
        if IX_ONLY_RE.match(line):

            if (
                i + 1 < end
                and RELATED_ONLY_RE.match(
                    lines[i + 1]
                )
            ):

                return i + 1

        # Practical related questions ...
        if RELATED_ONLY_RE.match(line):

            return i

    return None


# ============================================================
# FIND REFERENCES
# ============================================================

def find_references(
    lines,
    start,
    end
):

    for i in range(
        start,
        end
    ):

        line = lines[i]

        if REFERENCES_RE.match(
            line
        ):

            return i

    return None


# ============================================================
# CLEAN NOTE
# ============================================================

def remove_sample_note(lines):

    """
    Everything before the first question in the IX section
    is the teacher note.

    Therefore:

        Note: ...
        Teachers must ...
        identified CO.

    is ignored automatically.
    """

    for i, line in enumerate(
        lines
    ):

        if QUESTION_RE.match(line):

            return lines[i:]

    return []


# ============================================================
# PARSE QUESTION SECTION
# ============================================================

def parse_questions(
    lines,
    question_type
):

    questions = []

    current = None

    for line in lines:

        if line == "<PAGE_BREAK>":
            continue

        line = line.strip()

        if not line:
            continue

        # ----------------------------------------------------
        # Ignore answer-space material
        # ----------------------------------------------------

        if is_dot_line(line):
            continue

        if is_answer_marker(line):
            continue

        if is_blank_instruction(line):
            continue

        # ----------------------------------------------------
        # Remove repeated page headers even if variants occur
        # ----------------------------------------------------

        if is_page_header(line):
            continue

        if is_course_code(line):
            continue

        if is_scheme(line):
            continue

        # ----------------------------------------------------
        # A new numbered question
        #
        # Handles:
        #
        # 1.
        # 1)
        # 2.
        # 2)
        # ----------------------------------------------------

        match = QUESTION_RE.match(
            line
        )

        if match:

            if current is not None:
                questions.append(
                    current
                )

            current = match.group(
                2
            ).strip()

            continue

        # ----------------------------------------------------
        # Bullet question
        # ----------------------------------------------------

        bullet = BULLET_RE.match(
            line
        )

        if bullet:

            if current is not None:
                questions.append(
                    current
                )

            current = bullet.group(
                1
            ).strip()

            continue

        # ----------------------------------------------------
        # Lettered subpart
        #
        # a. ...
        # a) ...
        # b. ...
        # b) ...
        # ----------------------------------------------------

        letter = LETTER_SUBPART_RE.match(
            line
        )

        if letter:

            if current is not None:

                current += (
                    " "
                    + letter.group(2).strip()
                )

            continue

        # ----------------------------------------------------
        # Roman subpart
        #
        # i. ...
        # ii. ...
        # ----------------------------------------------------

        roman = ROMAN_SUBPART_RE.match(
            line
        )

        if roman:

            if current is not None:

                current += (
                    " "
                    + roman.group(2).strip()
                )

            continue

        # ----------------------------------------------------
        # Ignore NOTE text
        # ----------------------------------------------------

        if NOTE_RE.match(line):

            continue

        # ----------------------------------------------------
        # Continuation
        # ----------------------------------------------------

        if current is not None:

            current += (
                " "
                + line
            )

    if current is not None:

        questions.append(
            current
        )

    return [
        clean_question(q)
        for q in questions
        if clean_question(q)
    ]


# ============================================================
# QUESTION CLEANUP
# ============================================================

def clean_question(text):

    # Remove page-header variants accidentally embedded in
    # a continuation line.
    text = re.sub(
        r"statistical\s*:?\s*modelling\s+for\s+machine\s+learning",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"course\s+code\s*:\s*313307",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"msbte\s*/?\s*k\s*-\s*scheme",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove spaces before punctuation.
    text = re.sub(
        r"\s+([,.;:?)])",
        r"\1",
        text
    )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# PROCESS ONE PRACTICAL
# ============================================================

def process_practical(
    lines,
    practical
):

    number = practical["number"]
    start = practical["start"]
    end = practical["end"]

    # --------------------------------------------------------
    # 1. Practical Significance
    # --------------------------------------------------------

    significance = find_significance(
        lines,
        start,
        end
    )

    if significance is None:

        return None, (
            "Practical Significance marker not found"
        )

    # --------------------------------------------------------
    # 2. Title
    # --------------------------------------------------------

    title = extract_title(
        lines,
        start,
        significance,
        number
    )

    # --------------------------------------------------------
    # 3. Exercise marker
    # --------------------------------------------------------

    exercise = find_exercise(
        lines,
        significance,
        end
    )

    if exercise is None:

        return None, (
            "VIII. Exercise marker not found"
        )

    # --------------------------------------------------------
    # 4. Practical-related Questions marker
    # --------------------------------------------------------

    related = find_related(
        lines,
        exercise,
        end
    )

    if related is None:

        return None, (
            "IX. Practical related Questions marker not found"
        )

    # --------------------------------------------------------
    # 5. References
    # --------------------------------------------------------

    references = find_references(
        lines,
        related,
        end
    )

    # --------------------------------------------------------
    # 6. Exercise text
    # --------------------------------------------------------

    exercise_lines = lines[
        exercise + 1:
        related
    ]

    # --------------------------------------------------------
    # 7. Practical-related text
    # --------------------------------------------------------

    if references is not None:

        related_lines = lines[
            related + 1:
            references
        ]

    else:

        related_lines = lines[
            related + 1:
            end
        ]

    # --------------------------------------------------------
    # 8. Parse
    # --------------------------------------------------------

    exercises = parse_questions(
        exercise_lines,
        "exercise"
    )

    related_questions = parse_questions(
        remove_sample_note(
            related_lines
        ),
        "related"
    )

    # --------------------------------------------------------
    # 9. Format
    # --------------------------------------------------------

    output = []

    output.append(
        title
    )

    output.append("")

    output.append(
        "Exercises"
    )

    for index, question in enumerate(
        exercises,
        start=1
    ):

        output.append(
            f"* E{number}.{index}: "
            f"{question}"
        )

    output.append("")

    output.append(
        "Practical-Related Questions"
    )

    for index, question in enumerate(
        related_questions,
        start=1
    ):

        output.append(
            f"* P{number}.{index}: "
            f"{question}"
        )

    output.append("")

    output.append(
        "-" * 80
    )

    return "\n".join(output), {
        "number": number,
        "title": title,
        "exercises": exercises,
        "related": related_questions
    }


# ============================================================
# MAIN
# ============================================================

def main():

    input_pdf = INPUT_PDF
    output_txt = OUTPUT_TXT

    if len(sys.argv) >= 2:
        input_pdf = sys.argv[1]

    if len(sys.argv) >= 3:
        output_txt = sys.argv[2]

    if not os.path.exists(
        input_pdf
    ):

        print(
            f"ERROR: PDF not found: {input_pdf}"
        )

        sys.exit(1)

    print(
        f"Reading PDF: {input_pdf}"
    )

    pages = extract_pages(
        input_pdf
    )

    print(
        f"Pages extracted: {len(pages)}"
    )

    lines = flatten_pages(
        pages
    )

    practicals = find_practicals(
        lines
    )

    print(
        f"Practicals detected: "
        f"{len(practicals)}"
    )

    if not practicals:

        print(
            "ERROR: No Practical No.N markers found."
        )

        sys.exit(1)

    output_blocks = []

    successful = 0
    failed = 0

    for practical in practicals:

        result, info = process_practical(
            lines,
            practical
        )

        number = practical[
            "number"
        ]

        if result is None:

            failed += 1

            print(
                f"[FAILED] Practical {number}: "
                f"{info}"
            )

            continue

        successful += 1

        print(
            f"[OK] Practical {number}: "
            f"{len(info['exercises'])} exercises, "
            f"{len(info['related'])} related questions"
        )

        output_blocks.append(
            result
        )

    final_text = "\n\n".join(
        output_blocks
    )

    final_text = re.sub(
        r"\n-{20,}\s*$",
        "",
        final_text
    ).rstrip()

    with open(
        output_txt,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            final_text
        )

        file.write("\n")

    print()
    print("=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(
        f"Detected   : {len(practicals)}"
    )
    print(
        f"Successful : {successful}"
    )
    print(
        f"Failed     : {failed}"
    )
    print(
        f"Output     : {os.path.abspath(output_txt)}"
    )


if __name__ == "__main__":
    main()
