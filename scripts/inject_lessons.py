import json
import os
import shutil

PT_FILE = "content/lessons_pt.json"
EN_FILE = "content/lessons_en.json"
MAPPING_FILE = "content/id_mapping.json"

new_lessons_pt = {
    "Aula 7: Como instalar o Python?": [
        {
            "type": "theory",
            "title": "Aula X: O que é o PIP?",
            "description": "Entenda o que é o gerenciador de pacotes do ecossistema Python.",
            "content": "O **PIP** (Pip Installs Packages) é o gerenciador de pacotes oficial do Python. Ele permite que você instale, atualize e remova bibliotecas e ferramentas de terceiros criadas pela comunidade (disponíveis no PyPI - Python Package Index) com um simples comando no terminal, como `pip install requests`.",
            "quiz": {
                "question": "O que é o PIP no ecossistema Python?",
                "options": [
                    "Um gerenciador de pacotes",
                    "Um editor de código (IDE)",
                    "Um navegador web",
                    "Um banco de dados"
                ],
                "answer": 0
            }
        }
    ],
    "Aula 9: Comentários e Documentação": [
        {
            "type": "theory",
            "title": "Aula X: Quiz - Símbolo de Comentário",
            "description": "Teste seus conhecimentos sobre comentários em Python.",
            "content": "Lembre-se: Comentários são partes do código que o Python ignora. Eles servem para ajudar os humanos a entenderem o que o código faz.",
            "quiz": {
                "question": "Qual símbolo é usado para criar comentários de linha única em Python?",
                "options": ["#", "/*", "//", "--"],
                "answer": 0
            }
        },
        {
            "type": "theory",
            "title": "Aula X: Quiz - O Melhor Comentário",
            "description": "Aprenda a escrever comentários úteis e não redundantes.",
            "content": "Bons comentários explicam o **porquê** de uma ação, e não o **quê**. Se o código já é óbvio, não o comente narrando o óbvio.",
            "quiz": {
                "question": "Qual destes é o MELHOR comentário para o código: total = preco + imposto?",
                "options": [
                    "# Calcule o total final incluindo imposto",
                    "# Operação matemática",
                    "# Adicione preço e impostos",
                    "# total é igual ao preço mais impostos"
                ],
                "answer": 0
            }
        },
        {
            "type": "theory",
            "title": "Aula X: Quiz - Quando Comentar?",
            "description": "Reflita sobre a frequência ideal de comentários.",
            "content": "Um código limpo (Clean Code) deve tentar ser autoexplicativo através de bons nomes de variáveis. O comentário é um recurso para quando a lógica for inevitavelmente complexa.",
            "quiz": {
                "question": "Quando você deve escrever comentários no seu código?",
                "options": [
                    "Nunca, um bom código deve ser autoexplicativo.",
                    "Apenas no início do arquivo.",
                    "Em cada linha.",
                    "Somente quando o código for complexo ou o propósito não for óbvio."
                ],
                "answer": 3
            }
        },
        {
            "type": "theory",
            "title": "Aula X: Quiz - Execução de Comentários",
            "description": "O que o interpretador acha dos seus comentários?",
            "content": "O interpretador do Python é muito rápido, e ele simplesmente descarta os comentários antes de executar a lógica matemática.",
            "quiz": {
                "question": "O que acontece com os comentários quando o Python executa seu programa?",
                "options": [
                    "Eles são exibidos ao usuário.",
                    "Eles são convertidos em print.",
                    "Eles são ignorados pelo Python.",
                    "Deixam o programa mais lento."
                ],
                "answer": 2
            }
        }
    ],
    "Aula 11: Variáveis e Textos (Strings)": [
        {
            "type": "theory",
            "title": "Aula X: Quiz - Exibir Textos",
            "description": "Revise como mostrar mensagens para o usuário.",
            "content": "A função mais fundamental que aprendemos é aquela que manda uma mensagem do código para a tela do computador.",
            "quiz": {
                "question": "Qual função você usa para exibir texto na tela em Python?",
                "options": ["out()", "echo", "print()", "display()"],
                "answer": 2
            }
        },
        {
            "type": "theory",
            "title": "Aula X: Quiz - Atribuindo Novos Valores",
            "description": "O que acontece quando você reutiliza uma variável?",
            "content": "Variáveis recebem esse nome porque seus valores podem variar com o tempo!",
            "quiz": {
                "question": "O que acontece quando você atribui um novo valor a uma variável existente?",
                "options": [
                    "Cria uma nova variável com um nome diferente.",
                    "Ocorre um erro porque não podem ser alteradas.",
                    "O valor antigo é substituído pelo novo valor.",
                    "Ambos os valores são armazenados."
                ],
                "answer": 2
            }
        },
        {
            "type": "theory",
            "title": "Aula X: Quiz - F-Strings 1",
            "description": "Analisando a estrutura das f-strings.",
            "content": "As f-strings injetam valores de variáveis direto em textos de forma elegante.",
            "quiz": {
                "question": "O que este código faz: print(f'Hello, {name}!')?",
                "options": [
                    "Causa um erro",
                    "Cria uma nova variável",
                    "Imprime o texto literal",
                    "Imprime 'Hello,' seguido pelo valor da variável"
                ],
                "answer": 3
            }
        },
        {
            "type": "theory",
            "title": "Aula X: Quiz - F-Strings 2",
            "description": "Adivinhe a saída do código usando f-strings.",
            "content": "Lembre-se que as chaves `{}` são substituídas pelos valores.",
            "quiz": {
                "question": "Qual será o resultado deste código?\nnome = 'Alice'\nidade = 25\nprint(f'Olá, {nome}! Você tem {idade} anos.')",
                "options": [
                    "Olá, Alice! Você tem 25 anos.",
                    "Ocorrerá um erro.",
                    "Olá, [nome]! Você tem [idade] anos de idade.",
                    "Olá, {nome}! Você tem {age} anos de idade."
                ],
                "answer": 0
            }
        }
    ],
    "Aula 12: Números Inteiros (Int)": [
        {
            "type": "theory",
            "title": "Aula X: Quiz - Criando uma Variável",
            "description": "Como declaramos variáveis em Python?",
            "content": "Diferente de C, Java ou JavaScript, o Python não precisa de palavras como `int` ou `var` antes de declarar a variável. Ele descobre o tipo sozinho!",
            "quiz": {
                "question": "Qual é a maneira correta de criar uma variável chamada 'age' com o valor 25?",
                "options": ["age = 25", "var age = 25", "int age = 25", "age := 25"],
                "answer": 0
            }
        }
    ],
    "Aula 15: Operadores Aritméticos": [
        {
            "type": "theory",
            "title": "Aula X: Quiz - Operadores de Atribuição",
            "description": "Descubra como somar e guardar de forma abreviada.",
            "content": "Você já sabe que `pontuacao = pontuacao + 10` funciona. Mas existe um atalho muito usado por programadores experientes!",
            "quiz": {
                "question": "Qual destas é a maneira correta e abreviada de aumentar a 'pontuação' de uma variável em 10 pontos?",
                "options": ["10 += pontuação", "pontuação += 10", "pontuação = + 10", "pontuação + 10"],
                "answer": 1
            }
        }
    ],
    "Aula 19: O Interpretador e o Modo Interativo": [
        {
            "type": "theory",
            "title": "Aula X: Quiz - Entrada do Usuário",
            "description": "Como escutar o que o usuário digita?",
            "content": "Programas não precisam ser estáticos. Eles podem conversar com o usuário pedindo informações pelo teclado.",
            "quiz": {
                "question": "Qual função permite que seu programa receba uma entrada do usuário via teclado?",
                "options": ["get()", "read()", "scan()", "input()"],
                "answer": 3
            }
        }
    ],
    "Aula 26: Atribuição Múltipla e Laço While": [
        {
            "type": "theory",
            "title": "Aula X: Indentação e Blocos de Código",
            "description": "Como o Python organiza a estrutura lógica do seu programa.",
            "content": "Ao invés de usar chaves `{}` como C ou Java, o Python usa os espaços em branco antes da linha (**indentação**) para dizer que um código está 'dentro' de um laço ou condição. É recomendável usar sempre 4 espaços.",
            "quiz": {
                "question": "Como o Python agrupa código em blocos?",
                "options": [
                    "Usando parênteses ( )",
                    "Usando colchetes [ ]",
                    "Usando chaves { }",
                    "Usando indentação (espaços ou tabulações)"
                ],
                "answer": 3
            }
        },
        {
            "type": "theory",
            "title": "Aula X: Quiz - Tamanho da Indentação",
            "description": "Qual é a convenção recomendada (PEP 8)?",
            "content": "Você pode usar 2 espaços, 4 espaços, ou Tab. Mas a comunidade oficial tem uma preferência clara.",
            "quiz": {
                "question": "Qual é o tamanho de indentação recomendado oficialmente em Python?",
                "options": ["4 espaços", "Não importa", "8 espaços", "2 espaços"],
                "answer": 0
            }
        },
        {
            "type": "theory",
            "title": "Aula X: Quiz - Indentação Inconsistente",
            "description": "O que acontece se você misturar espaços e Tabs?",
            "content": "Se o seu código usar 4 espaços em um lugar e Tab em outro dentro do mesmo bloco, o Python não vai entender quem pertence a quem.",
            "quiz": {
                "question": "O que acontece se você tiver indentação inconsistente em Python?",
                "options": [
                    "Python irá consertar isso automaticamente",
                    "Python irá gerar um IndentationError",
                    "O programa será executado, mas com avisos",
                    "Nada acontece, é apenas uma preferência de estilo"
                ],
                "answer": 1
            }
        }
    ]
}

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
    "Lesson 11: Variables and Texts (Strings)": [
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
    "Lesson 12: Integer Numbers (Int)": [
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
    "Lesson 19: The Interpreter and Interactive Mode": [
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

def update_lessons(file_path, new_lessons_dict):
    print(f"Processing {file_path}...")
    shutil.copy(file_path, file_path + ".bak")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    lessons = data["lessons"]
    
    # We will build a new list of lessons, injecting when we match a title
    new_lesson_list = []
    
    for l in lessons:
        new_lesson_list.append(l)
        title = l.get("title", "")
        
        if title in new_lessons_dict:
            to_insert = new_lessons_dict[title]
            print(f"-> Inserting {len(to_insert)} new lessons after '{title}'")
            for item in to_insert:
                new_lesson_list.append(item.copy())
                
    # Now we re-enumerate IDs and adjust titles to match "Aula [ID]: ..."
    mapping = {}
    
    for i, l in enumerate(new_lesson_list):
        old_id = l.get("id", None)
        if old_id is not None:
            # multiple new lessons will map correctly since we are only mapping old_id when the lesson is original
            mapping[str(old_id)] = i
            
        l["id"] = i
        
        title = l["title"]
        if title.startswith("Aula ") or title.startswith("Lesson "):
            parts = title.split(":", 1)
            if len(parts) == 2:
                prefix = parts[0]
                if prefix.startswith("Aula ") and prefix.split(" ")[1].isdigit() or prefix == "Aula X":
                    l["title"] = f"Aula {i}:{parts[1]}"
                elif prefix.startswith("Lesson ") and prefix.split(" ")[1].isdigit() or prefix == "Lesson X":
                    l["title"] = f"Lesson {i}:{parts[1]}"
                    
    data["lessons"] = new_lesson_list
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {file_path}. Total lessons: {len(new_lesson_list)}")
    return mapping

mapping_pt = update_lessons(PT_FILE, new_lessons_pt)
mapping_en = update_lessons(EN_FILE, new_lessons_en)

with open(MAPPING_FILE, "w", encoding="utf-8") as f:
    json.dump(mapping_pt, f, indent=2)
print(f"Saved ID mapping to {MAPPING_FILE}")
