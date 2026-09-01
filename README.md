### PDF Lab Manual Extractor

A lightweight Python tool that automatically extracts **Exercises** and **Practical-Related Questions** from university lab manuals and compiles them into a clean, easy-to-read text file. 

This script is specifically optimized to filter out repetitive headers, course codes, and blank answer spaces, leaving you with just the questions you need. 

### 🚀 Features

* 📋 **Automatic Extraction:** Pulls "Exercises" and "Practical-Related Questions" section-by-section.
* 🧹 **Smart Cleanup:** Automatically removes redundant headers like *“Statistical Modelling for Machine Learning”*, *“MSBTE K-Scheme”*, and lines of blank underscores/dots.
* 🔢 **Clean Labeling:** Automatically formats and re-indexes questions (e.g., E1.1 for Exercise 1, Question 1).

### 🛠️ Prerequisites

Before running the script, make sure you have **Python 3** installed on your computer. 

This script uses the **PyMuPDF** library to read PDF documents. 

### 💻 Installation & Setup

Follow these simple steps to set up the project on your local machine: 

### 1. Open Your Terminal

Open your terminal (Linux/Mac) or Command Prompt (Windows). 

### 2. Set Up a Virtual Environment (Recommended)

To keep your computer organized, create and activate an isolated virtual environment: 

```bash

# Create the environment
python3 -m venv myenv

# Activate it (Linux/Mac)
source myenv/bin/activate

# Activate it (Windows Command Prompt)
myenv\Scripts\activate
```
### 3. Install PyMuPDF

Once your environment is active, install the required library: 

```bash
pip install PyMuPDF
```

### 📖 How to Use

### Step 1: Prepare Your Files

Place the lab manual PDF you want to extract text from inside the same folder as the script. Rename your PDF file to input.pdf. 

```text

your-project-folder/
├── ManualQuestionExtractor.py       (This script)
├── input.pdf          (Your PDF manual)
└── myenv/             (Your virtual environment folder)
```

### Step 2: Run the Script

Execute the Python file from your terminal: 

```bash

python3 extractor.py
```

### Step 3: Get Your Output

Once the process is complete, a new text file named extracted_practicals.txt will appear in your folder containing all the sorted questions! 

### ⚙️ Advanced Usage (Optional)

If you don't want to rename your files to input.pdf and extracted_practicals.txt, you can pass custom filenames directly into the terminal command: 

```bash

python3 ManualQuestionExtractor.py my_manual.pdf my_output_questions.txt
```

### 📝 Example Output Format

The generated text file will look like this: 

```text

Practical 1: .....

Exercises
* E1.1: .....
* E1.2: ......

Practical-Related Questions
* P1.1: ......
* P1.2: ......

--------------------------------------------------------------------------------
```
