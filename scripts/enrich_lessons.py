import json

PT_UPDATES = {
    "O que é o PIP?": {
        "content": "O **PIP** (Pip Installs Packages) é o gerenciador de pacotes padrão do ecossistema Python. Imagine-o como a 'App Store' ou 'Google Play' para os desenvolvedores. Quando você precisa de uma funcionalidade que não vem por padrão no Python (como conectar a um banco de dados na nuvem, criar gráficos complexos ou criar interfaces gráficas), você usa o PIP no terminal para baixar essas ferramentas de terceiros diretamente do **PyPI** (Python Package Index). Isso economiza milhares de horas de trabalho!",
        "example": "# Instalando uma biblioteca famosa para fazer requisições na web\npip install requests\n\n# Instalando o Pandas para análise de dados\npip install pandas"
    },
    "Símbolo de Comentário": {
        "content": "Comentários são anotações valiosas que fazemos no código fonte para que outros desenvolvedores (ou nós mesmos no futuro) possamos entender o raciocínio por trás de uma lógica complexa. Tudo que for escrito após o símbolo de comentário será completamente ignorado pelo interpretador do Python, não afetando a velocidade ou o resultado final do programa.",
        "example": "# Isso é um comentário de linha única em Python.\nprint(\"Olá!\")  # Você também pode colocar o comentário após um comando válido."
    },
    "O Melhor Comentário": {
        "content": "Um dos maiores erros de programadores iniciantes é comentar o que é óbvio. Um bom comentário deve explicar o **porquê** de algo ter sido feito, a intenção de negócio, ou alertar sobre alguma peculiaridade. O seu código, através de bons nomes de variáveis, já deve ser capaz de explicar o **quê** está acontecendo. Se você precisa comentar cada linha, talvez o seu código precise ser reescrito para ficar mais legível.",
        "example": "# RUIM (Redundante):\n# Soma preco e imposto e guarda em total\ntotal = preco + imposto\n\n# BOM (Explica o contexto):\n# O imposto de 15% é obrigatório para vendas interestaduais (Lei 123/45)\ntotal = preco + imposto"
    },
    "Quando Comentar?": {
        "content": "A regra de ouro (Clean Code) diz que comentários devem ser usados apenas quando o código por si só não for capaz de expressar sua intenção. Códigos que descrevem regras matemáticas altamente complexas, integrações com sistemas legados ou pequenos 'macetes' técnicos para contornar bugs de outras bibliotecas são excelentes candidatos para receberem documentação.",
        "example": "# WORKAROUND: Foi necessário aguardar 2 segundos aqui porque a API do banco sempre atrasa a resposta na primeira tentativa de conexão.\nimport time\ntime.sleep(2)\nconectar_banco()"
    },
    "Execução de Comentários": {
        "content": "Diferente das strings literais (que são carregadas na memória), comentários iniciados com `#` são removidos da execução antes mesmo do programa começar a rodar a fundo. Isso significa que você pode ter milhares de linhas de comentários explicando um algoritmo complexo sem nenhum peso ou lentidão adicional no seu aplicativo.",
        "example": "# Você pode escrever um parágrafo inteiro de explicação aqui.\n# O Python não gastará nem meio milissegundo para ignorar tudo isso.\n# Portanto, não tenha medo de documentar o seu projeto!\nprint(\"O código continua rápido!\")"
    },
    "Exibir Textos": {
        "content": "A função mais primordial da programação é a saída de dados (`output`). No Python, utilizamos a função embutida `print()` para jogar textos, números e resultados na saída padrão (geralmente o terminal ou console). Diferente de outras linguagens como C ou Java, o print do Python já quebra a linha automaticamente ao final da execução.",
        "example": "print(\"Esta é a primeira linha.\")\nprint(\"Esta aparecerá na linha de baixo automaticamente!\")\n\n# Podemos imprimir vários valores de uma vez separando por vírgulas:\nprint(\"Meu nome é\", \"Alice\", \"e tenho\", 25, \"anos.\")"
    },
    "Atribuindo Novos Valores": {
        "content": "O conceito de **Variável** na programação é literal: seu valor pode variar! Quando você diz que `x = 10` e, linhas abaixo, diz que `x = 20`, o valor 10 é descartado e o 20 assume o seu lugar na memória. O Python tem um 'Lixeiro Automático' (Garbage Collector) que apaga dados antigos que não estão mais sendo usados para economizar RAM.",
        "example": "pontos = 100\nprint(f\"Pontos Iniciais: {pontos}\")  # Imprime 100\n\n# O jogador sofreu dano\npontos = 50\nprint(f\"Pontos Atuais: {pontos}\")  # Imprime 50 (o 100 foi esquecido)"
    },
    "F-Strings 1": {
        "content": "Lançadas no Python 3.6, as **F-Strings** revolucionaram a forma de manipular textos. Ao colocar um simples `f` antes das aspas de um texto, você transforma aquela string em um template dinâmico, permitindo injetar resultados matemáticos, funções ou variáveis diretamente no texto usando chaves `{}`.",
        "example": "heroi = \"Link\"\ncoracoes = 3\n# A f-string avalia tudo que está nas chaves\nprint(f\"O herói {heroi} tem {coracoes * 2} pontos de vida no total.\")"
    },
    "F-Strings 2": {
        "content": "Um cuidado especial com as F-Strings: você pode usar tanto aspas simples quanto duplas para defini-las. No entanto, lembre-se que se a variável não estiver definida antes da chamada, o código irá falhar imediatamente.",
        "example": "produto = \"Teclado Mecânico\"\npreco = 250.00\n# Formatação de casas decimais também é suportada!\nprint(f\"Oferta: {produto} por apenas R$ {preco:.2f}\")"
    },
    "Criando uma Variável": {
        "content": "O Python é uma linguagem de tipagem dinâmica. Isso quer dizer que o interpretador deduz se a variável é um texto (string) ou número inteiro (int) dependendo do que está depois do sinal de igual `=`. Por isso, evite nomes mágicos como `a`, `b` e declare o que ela representa.",
        "example": "# Python descobre os tipos automaticamente:\nidade = 25          # inteiro (int)\nnome = \"Bob\"        # texto (str)\naltura = 1.80       # decimal (float)\n\nprint(type(idade))  # <class 'int'>"
    },
    "Operadores de Atribuição": {
        "content": "Programadores gostam de atalhos. Ao invés de escrever `moedas = moedas + 5`, o Python permite combinar a operação aritmética e a atribuição na mesma tacada usando `+=`. Você também pode fazer o mesmo com subtração (`-=`), multiplicação (`*=`) e divisão (`/=`).",
        "example": "nivel = 5\nnivel += 1   # Mesma coisa que: nivel = nivel + 1\nprint(nivel) # Imprime 6\n\nvida = 100\nvida -= 20   # Mesma coisa que: vida = vida - 20\nprint(vida)  # Imprime 80"
    },
    "Entrada do Usuário": {
        "content": "A função `input()` congela a execução do programa e aguarda o usuário digitar algo e pressionar 'Enter'. Todo o texto digitado é devolvido em formato de String e pode ser guardado numa variável para tornar o seu script verdadeiramente interativo!",
        "example": "# O texto entre parênteses aparece na tela pedindo a ação\nnome = input(\"Qual é o seu nome herói? \")\n\nprint(f\"Bem-vindo à aventura, {nome}!\")"
    },
    "Indentação e Blocos de Código": {
        "content": "Linguagens como JavaScript e C utilizam chaves `{}` para marcar onde começa e onde termina uma condição `if` ou um laço `for`. No Python, o organizador visual É a própria sintaxe. Nós recuamos o texto para a direita para indicar que aquele grupo de códigos pertence à condição acima dele.",
        "example": "chefe_derrotado = True\n\nif chefe_derrotado:\n    # As próximas duas linhas estão 'dentro' do if por causa do recuo\n    print(\"Parabéns, você salvou a princesa!\")\n    print(\"Recompensa: +500 XP\")\n\n# Esta linha não tem recuo, roda independente do if\nprint(\"Fim de Jogo.\")"
    },
    "Tamanho da Indentação": {
        "content": "O Guia Oficial de Estilo do Python (PEP 8) é uma espécie de 'Bíblia' da organização do código. E ele é categórico: o recuo de blocos deve ser feito usando exatos **4 espaços em branco**. A maioria das IDEs modernas já configuram a tecla `Tab` para inserir 4 espaços automaticamente para você!",
        "example": "# Um bloco de código perfeito:\ndef iniciar_jogo():\n    # <- 4 espaços aqui\n    pontos = 0\n    vidas = 3\n    print(\"Jogo carregado.\")"
    },
    "Indentação Inconsistente": {
        "content": "Um dos erros mais frustrantes para quem está começando é o temido `IndentationError`. Ele não perdoa! Se você usar 4 espaços em uma linha e 5 espaços na linha seguinte dentro do mesmo bloco, o interpretador irá interromper o seu programa imediatamente.",
        "example": "status = \"Ativo\"\n\nif status == \"Ativo\":\n    print(\"Sistema online.\")  # Certo: 4 espaços\n    # print(\"Conectando...\")  # Se tivesse 5 espaços geraria erro."
    }
}

EN_UPDATES = {
    "What is PIP?": {
        "content": "**PIP** (Pip Installs Packages) is the standard package manager for the Python ecosystem. Think of it as the 'App Store' or 'Google Play' for developers. When you need functionality that doesn't come standard with Python (like connecting to a cloud database, creating complex charts, or GUI apps), you use PIP in the terminal to download these third-party tools directly from **PyPI** (Python Package Index). It saves thousands of hours of work!",
        "example": "# Installing a famous library for web requests\npip install requests\n\n# Installing Pandas for data analysis\npip install pandas"
    },
    "Comment Symbol": {
        "content": "Comments are valuable notes we write in the source code so that other developers (or ourselves in the future) can understand the reasoning behind complex logic. Anything written after the comment symbol will be completely ignored by the Python interpreter, not affecting the speed or final result of the program.",
        "example": "# This is a single-line comment in Python.\nprint(\"Hello!\")  # You can also place the comment after a valid command."
    },
    "The Best Comment": {
        "content": "One of the biggest mistakes beginner programmers make is commenting the obvious. A good comment should explain **why** something was done, the business intent, or warn about a peculiarity. Your code, through good variable names, should already explain **what** is happening. If you have to comment every line, perhaps your code needs to be rewritten to be more readable.",
        "example": "# BAD (Redundant):\n# Adds price and tax and saves in total\ntotal = price + tax\n\n# GOOD (Explains context):\n# The 15% tax is mandatory for interstate sales (Law 123/45)\ntotal = price + tax"
    },
    "When to Comment?": {
        "content": "The golden rule (Clean Code) states that comments should only be used when the code itself cannot express its intent. Code that describes highly complex mathematical rules, integrations with legacy systems, or small technical 'hacks' to bypass bugs in other libraries are excellent candidates for documentation.",
        "example": "# WORKAROUND: We had to wait 2 seconds here because the bank's API always delays the response on the first connection attempt.\nimport time\ntime.sleep(2)\nconnect_db()"
    },
    "Comment Execution": {
        "content": "Unlike string literals (which are loaded into memory), comments starting with `#` are removed from execution before the program even begins to run deeply. This means you can have thousands of lines of comments explaining a complex algorithm with absolutely no performance weight or slowdown in your application.",
        "example": "# You can write an entire paragraph of explanation here.\n# Python won't spend even half a millisecond ignoring all this.\n# Therefore, don't be afraid to document your project!\nprint(\"The code remains fast!\")"
    },
    "Displaying Texts": {
        "content": "The most fundamental function in programming is data output. In Python, we use the built-in `print()` function to output texts, numbers, and results to standard output (usually the terminal or console). Unlike other languages like C or Java, Python's print automatically adds a line break at the end of execution.",
        "example": "print(\"This is the first line.\")\nprint(\"This will appear on the bottom line automatically!\")\n\n# We can print multiple values at once separated by commas:\nprint(\"My name is\", \"Alice\", \"and I am\", 25, \"years old.\")"
    },
    "Assigning New Values": {
        "content": "The concept of a **Variable** in programming is literal: its value can vary! When you say `x = 10` and lines below say `x = 20`, the value 10 is discarded and 20 takes its place in memory. Python has an automatic 'Garbage Collector' that deletes old data that is no longer being used to save RAM.",
        "example": "points = 100\nprint(f\"Starting Points: {points}\")  # Prints 100\n\n# The player took damage\npoints = 50\nprint(f\"Current Points: {points}\")  # Prints 50 (100 was forgotten)"
    },
    "F-Strings 1": {
        "content": "Introduced in Python 3.6, **F-Strings** revolutionized text manipulation. By placing a simple `f` before the quotes of a text, you turn that string into a dynamic template, allowing you to inject mathematical results, functions, or variables directly into the text using curly braces `{}`.",
        "example": "hero = \"Link\"\nhearts = 3\n# The f-string evaluates everything inside the braces\nprint(f\"The hero {hero} has {hearts * 2} total health points.\")"
    },
    "F-Strings 2": {
        "content": "A special warning with F-Strings: you can use both single or double quotes to define them. However, remember that if the variable is not defined before the call, the code will fail immediately.",
        "example": "product = \"Mechanical Keyboard\"\nprice = 250.00\n# Decimal place formatting is also supported!\nprint(f\"Offer: {product} for only $ {price:.2f}\")"
    },
    "Creating a Variable": {
        "content": "Python is a dynamically typed language. This means the interpreter deduces whether the variable is text (string) or an integer number (int) depending on what is after the equals sign `=`. Because of this, avoid magic names like `a`, `b` and clearly state what it represents.",
        "example": "# Python automatically discovers the types:\nage = 25          # integer (int)\nname = \"Bob\"      # text (str)\nheight = 1.80     # decimal (float)\n\nprint(type(age))  # <class 'int'>"
    },
    "Assignment Operators": {
        "content": "Programmers love shortcuts. Instead of writing `coins = coins + 5`, Python allows you to combine the arithmetic operation and assignment in the same step using `+=`. You can also do the same with subtraction (`-=`), multiplication (`*=`), and division (`/=`).",
        "example": "level = 5\nlevel += 1   # Same as: level = level + 1\nprint(level) # Prints 6\n\nhealth = 100\nhealth -= 20   # Same as: health = health - 20\nprint(health)  # Prints 80"
    },
    "User Input": {
        "content": "The `input()` function freezes program execution and waits for the user to type something and press 'Enter'. All the text typed is returned as a String format and can be saved in a variable to make your script truly interactive!",
        "example": "# The text inside parentheses appears on screen asking for action\nname = input(\"What is your name hero? \")\n\nprint(f\"Welcome to the adventure, {name}!\")"
    },
    "Indentation and Code Blocks": {
        "content": "Languages like JavaScript and C use curly braces `{}` to mark where an `if` condition or `for` loop begins and ends. In Python, the visual organizer IS the syntax itself. We indent text to the right to indicate that that group of codes belongs to the condition above it.",
        "example": "boss_defeated = True\n\nif boss_defeated:\n    # The next two lines are 'inside' the if because of the indent\n    print(\"Congratulations, you saved the princess!\")\n    print(\"Reward: +500 XP\")\n\n# This line has no indent, it runs independent of the if\nprint(\"Game Over.\")"
    },
    "Indentation Size": {
        "content": "The official Python Style Guide (PEP 8) is sort of the 'Bible' of code organization. And it is categorical: block indentation must be done using exactly **4 blank spaces**. Most modern IDEs already configure the `Tab` key to insert 4 spaces automatically for you!",
        "example": "# A perfect block of code:\ndef start_game():\n    # <- 4 spaces here\n    score = 0\n    lives = 3\n    print(\"Game loaded.\")"
    },
    "Inconsistent Indentation": {
        "content": "One of the most frustrating errors for beginners is the dreaded `IndentationError`. It is unforgiving! If you use 4 spaces on one line and 5 spaces on the next line within the same block, the interpreter will stop your program immediately.",
        "example": "status = \"Active\"\n\nif status == \"Active\":\n    print(\"System online.\")   # Correct: 4 spaces\n    # print(\"Connecting...\")  # If it had 5 spaces it would raise an Indentation error."
    }
}

def enrich_lessons(filename, updates_dict):
    print(f"Enriching {filename}...")
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for l in data["lessons"]:
        title = l.get("title", "")
        # Find which update matches this title
        for key, enhancements in updates_dict.items():
            if key in title:
                print(f"Enhancing: {title}")
                l["content"] = enhancements["content"]
                l["example"] = enhancements["example"]
                break
                
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

enrich_lessons("content/lessons_pt.json", PT_UPDATES)
enrich_lessons("content/lessons_en.json", EN_UPDATES)
print("Finished enriching lessons!")
