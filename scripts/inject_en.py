import json
import os
import shutil

EN_FILE = "content/lessons_en.json"

new_lessons_en = {
    "Lesson 7: How to install Python?": [
        {
            "type": "theory",
            "title": "Lesson X: What is PIP?",
            "description": "Understand the package manager of the Python ecosystem.",
            "content": "**PIP** (Pip Installs Packages) is the official package manager for Python. It allows you to install, update, and remove third-party libraries and tools created by the community (available on PyPI - Python Package Index) with a simple terminal command like `pip install requests`.",
            "quiz": {
                "question": "What is PIP in the Python ecosystem?",
                "options": [
                    "A package manager",
                    "A code editor (IDE)",
                    "A web browser",
                    "A database"
                ],
                "answer": 0
            }
        }
    ],
    "Lesson 9: Comments and Documentation": [
        {
            "type": "theory",
            "title": "Lesson X: Quiz - Comment Symbol",
            "description": "Test your knowledge about comments in Python.",
            "content": "Remember: Comments are parts of the code that Python ignores. They help humans understand what the code does.",
            "quiz": {
                "question": "Which symbol is used to create single-line comments in Python?",
                "options": ["#", "/*", "//", "--"],
                "answer": 0
            }
        },
        {
            "type": "theory",
            "title": "Lesson X: Quiz - The Best Comment",
            "description": "Learn to write useful and non-redundant comments.",
            "content": "Good comments explain the **why** of an action, not the **what**. If the code is already obvious, don't comment narrating the obvious.",
            "quiz": {
                "question": "Which of these is the BEST comment for the code: total = price + tax?",
                "options": [
                    "# Calculate the final total including tax",
                    "# Math operation",
                    "# Add price and tax",
                    "# total equals price plus tax"
                ],
                "answer": 0
            }
        },
        {
            "type": "theory",
            "title": "Lesson X: Quiz - When to Comment?",
            "description": "Reflect on the ideal frequency of comments.",
            "content": "Clean Code should try to be self-explanatory through good variable names. Comments are for when the logic is inevitably complex.",
            "quiz": {
                "question": "When should you write comments in your code?",
                "options": [
                    "Never, good code should be self-explanatory.",
                    "Only at the beginning of the file.",
                    "On every line.",
                    "Only when the code is complex or the purpose is not obvious."
                ],
                "answer": 3
            }
        },
        {
            "type": "theory",
            "title": "Lesson X: Quiz - Comment Execution",
            "description": "What does the interpreter think of your comments?",
            "content": "The Python interpreter is very fast, and it simply discards comments before executing the mathematical logic.",
            "quiz": {
                "question": "What happens to comments when Python executes your program?",
                "options": [
                    "They are displayed to the user.",
                    "They are converted to print.",
                    "They are ignored by Python.",
                    "They make the program slower."
                ],
                "answer": 2
            }
        }
    ],
    "Class 8: Variables and Texts (Strings)": [
        {
            "type": "theory",
            "title": "Lesson X: Quiz - Displaying Texts",
            "description": "Review how to show messages to the user.",
            "content": "The most fundamental function we learned is the one that sends a message from the code to the computer screen.",
            "quiz": {
                "question": "Which function do you use to display text on the screen in Python?",
                "options": ["out()", "echo", "print()", "display()"],
                "answer": 2
            }
        },
        {
            "type": "theory",
            "title": "Lesson X: Quiz - Assigning New Values",
            "description": "What happens when you reuse a variable?",
            "content": "Variables get this name because their values can vary over time!",
            "quiz": {
                "question": "What happens when you assign a new value to an existing variable?",
                "options": [
                    "Creates a new variable with a different name.",
                    "An error occurs because they cannot be changed.",
                    "The old value is replaced by the new value.",
                    "Both values are stored."
                ],
                "answer": 2
            }
        },
        {
            "type": "theory",
            "title": "Lesson X: Quiz - F-Strings 1",
            "description": "Analyzing the structure of f-strings.",
            "content": "F-strings elegantly inject variable values straight into texts.",
            "quiz": {
                "question": "What does this code do: print(f'Hello, {name}!')?",
                "options": [
                    "Causes an error",
                    "Creates a new variable",
                    "Prints the literal text",
                    "Prints 'Hello,' followed by the variable value"
                ],
                "answer": 3
            }
        },
        {
            "type": "theory",
            "title": "Lesson X: Quiz - F-Strings 2",
            "description": "Guess the output of the code using f-strings.",
            "content": "Remember that braces `{}` are replaced by values.",
            "quiz": {
                "question": "What will be the result of this code?\nname = 'Alice'\nage = 25\nprint(f'Hello, {name}! You are {age} years old.')",
                "options": [
                    "Hello, Alice! You are 25 years old.",
                    "An error will occur.",
                    "Hello, [name]! You are [age] years old.",
                    "Hello, {name}! You are {age} years old."
                ],
                "answer": 0
            }
        }
    ],
    "Class 9: Integers (Int)": [
        {
            "type": "theory",
            "title": "Lesson X: Quiz - Creating a Variable",
            "description": "How do we declare variables in Python?",
            "content": "Unlike C, Java or JavaScript, Python does not need words like `int` or `var` before declaring the variable. It figures out the type itself!",
            "quiz": {
                "question": "What is the correct way to create a variable named 'age' with the value 25?",
                "options": ["age = 25", "var age = 25", "int age = 25", "age := 25"],
                "answer": 0
            }
        }
    ],
    "Lesson 15: Arithmetic Operators": [
        {
            "type": "theory",
            "title": "Lesson X: Quiz - Assignment Operators",
            "description": "Discover how to add and store in a short way.",
            "content": "You already know that `score = score + 10` works. But there is a shortcut heavily used by experienced programmers!",
            "quiz": {
                "question": "Which of these is the correct and shorthand way to increase a variable's 'score' by 10 points?",
                "options": ["10 += score", "score += 10", "score = + 10", "score + 10"],
                "answer": 1
            }
        }
    ],
    "Class 15: The Interpreter and the Interactive Mode": [
        {
            "type": "theory",
            "title": "Lesson X: Quiz - User Input",
            "description": "How to listen to what the user types?",
            "content": "Programs don't have to be static. They can converse with the user by asking for information via keyboard.",
            "quiz": {
                "question": "Which function allows your program to receive user input via keyboard?",
                "options": ["get()", "read()", "scan()", "input()"],
                "answer": 3
            }
        }
    ],
    "Lesson 26: Multiple Assignment and While Loop": [
        {
            "type": "theory",
            "title": "Lesson X: Indentation and Code Blocks",
            "description": "How Python organizes the logical structure of your program.",
            "content": "Instead of using braces `{}` like C or Java, Python uses whitespace before the line (**indentation**) to indicate that code is 'inside' a loop or condition. It's recommended to always use 4 spaces.",
            "quiz": {
                "question": "How does Python group code into blocks?",
                "options": [
                    "Using parentheses ( )",
                    "Using brackets [ ]",
                    "Using braces { }",
                    "Using indentation (spaces or tabs)"
                ],
                "answer": 3
            }
        },
        {
            "type": "theory",
            "title": "Lesson X: Quiz - Indentation Size",
            "description": "What is the recommended convention (PEP 8)?",
            "content": "You can use 2 spaces, 4 spaces, or Tab. But the official community has a clear preference.",
            "quiz": {
                "question": "What is the officially recommended indentation size in Python?",
                "options": ["4 spaces", "Doesn't matter", "8 spaces", "2 spaces"],
                "answer": 0
            }
        },
        {
            "type": "theory",
            "title": "Lesson X: Quiz - Inconsistent Indentation",
            "description": "What happens if you mix spaces and Tabs?",
            "content": "If your code uses 4 spaces in one place and Tab in another within the same block, Python won't understand who belongs to whom.",
            "quiz": {
                "question": "What happens if you have inconsistent indentation in Python?",
                "options": [
                    "Python will fix it automatically",
                    "Python will raise an IndentationError",
                    "The program will run, but with warnings",
                    "Nothing happens, it's just a style preference"
                ],
                "answer": 1
            }
        }
    ]
}

def update_lessons_en():
    print(f"Processing {EN_FILE}...")
    # Restore from bak
    shutil.copy(EN_FILE + ".bak", EN_FILE)
    
    with open(EN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    lessons = data["lessons"]
    
    new_lesson_list = []
    
    for l in lessons:
        new_lesson_list.append(l)
        title = l.get("title", "")
        
        if title in new_lessons_en:
            to_insert = new_lessons_en[title]
            print(f"-> Inserting {len(to_insert)} new lessons after '{title}'")
            for item in to_insert:
                new_lesson_list.append(item.copy())
                
    mapping = {}
    
    for i, l in enumerate(new_lesson_list):
        old_id = l.get("id", None)
        if old_id is not None:
            mapping[str(old_id)] = i
            
        l["id"] = i
        
        title = l["title"]
        if title.startswith("Lesson ") or title.startswith("Class "):
            parts = title.split(":", 1)
            if len(parts) == 2:
                prefix = parts[0]
                if prefix.startswith("Lesson ") and prefix.split(" ")[1].isdigit() or prefix == "Lesson X":
                    l["title"] = f"Lesson {i}:{parts[1]}"
                elif prefix.startswith("Class ") and prefix.split(" ")[1].isdigit() or prefix == "Class X":
                    l["title"] = f"Class {i}:{parts[1]}"
                    
    data["lessons"] = new_lesson_list
    
    with open(EN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {EN_FILE}. Total lessons: {len(new_lesson_list)}")
    return mapping

update_lessons_en()
