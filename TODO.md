# PyCompilerDesign TODO List

## Phase 1: Refactoring and Code Improvement - COMPLETED

- [x] **Integrate `python-fsa` code:**
    - [x] Copy relevant functions and classes from `python-fsa` into the `compiler/fsa` module.
    - [x] Refactor the integrated code to match the existing style and structure of `PyCompilerDesign`.
    - [x] Ensure all existing tests pass after integration.
- [x] **Code Quality and Refactoring:**
    - [x] Review and refactor the `compiler/fsa` module for clarity, efficiency, and adherence to Python best practices.
    - [x] Improve docstrings and add type hinting where missing.
    - [x] Analyze and optimize performance-critical sections.

## Phase 2: Lexical Analysis - COMPLETED

- [x] **Implement Lexer:**
    - [x] Design a `Lexer` class in a new `compiler/lexer.py` file.
    - [x] The lexer should take a string of source code as input.
    - [x] It should output a stream of tokens.
- [x] **Define Tokens:**
    - [x] Create a `Token` class or dataclass to represent lexical tokens (e.g., type, value, line number).
    - [x] Add `LET` token type.
    - [x] Add `WHITESPACE` token type.
    - [x] Add `LITERAL` token type.
- [x] **Regular Expressions for Tokens:**
    - [x] Define a set of regular expressions to identify different token types (e.g., keywords, identifiers, operators, literals).
- [x] **Testing the Lexer:**
    - [x] Create a new `tests/test_lexer.py` file.
    - [x] Write unit tests to verify that the lexer correctly tokenizes various inputs.
- [x] **Integrate CppLexer:**
    - [x] Copy `token.py` and `lexer.py` from `CppCompilerProject/src/lexer` to `PyCompilerDesign/compiler/lexer`.
    - [x] Update imports in `PyCompilerDesign/compiler/lexer/lexer.py` to correctly reference `token.py`.
    - [x] Modify `main.py` to use `CppLexer` for lexing operations.
- [x] **Symbol Table Integration:**
    - [x] Modify `CppLexer` to create and populate a symbol table with identifiers and their first occurrence.
    - [x] Update `tokenize_and_filter` to return both tokens and the symbol table.
    - [x] Update `lex_code` in `main.py` to display the symbol table.
- [x] **Token Generation Enhancements:**
    - [x] Modify `CppLexer` to generate `WHITESPACE` tokens.
    - [x] Modify `CppLexer` to generate `LITERAL` tokens for numbers, strings, characters, and booleans.

## Phase 3: Parsing - COMPLETED

- [x] **Implement Parser:**
    - [x] Design a `Parser` class in a new `compiler/parser.py` file.
    - [x] The parser should take a list of tokens as input.
    - [x] It should output an Abstract Syntax Tree (AST).
- [x] **Define AST Nodes:**
    - [x] Create classes to represent the different nodes of the AST (e.g., `Program`, `Statement`, `Expression`).
    - [x] Define `VariableDeclaration` and `AssignmentStatement` AST nodes.
- [x] **Implement Parsing Logic:**
    - [x] Implement methods in the `Parser` class to parse the different grammatical structures of the language (e.g., `parse_program`, `parse_statement`, `parse_expression`).
    - [x] Update `parse_statement` to handle `let` declarations and assignments.
    - [x] Implement `_parse_variable_declaration` and `_parse_assignment_statement` methods.
- [x] **Testing the Parser:**
    - [x] Create a new `tests/test_parser.py` file.
    - [x] Write unit tests to verify that the parser correctly constructs the AST for various inputs.
- [x] **Improve Whitespace Handling in Parser:**
    - [x] Modify `_peek_token` to skip `WHITESPACE` tokens.
    - [x] Add `_skip_whitespace()` calls in `_parse_variable_declaration`, `_parse_assignment_statement`, `_parse_primary_expression`, and `parse_expression`.

## Phase 4: FSA Core Integration and Improvement - COMPLETED

- [x] **4.1 Understand `python-fsa`'s FSA Core:**
    - [x] Read relevant files in `E:\Mema-Lab\python-fsa` to identify core FSA logic (NFA, DFA, conversion, minimization).
    - [x] Analyze data structures for states, transitions, and alphabets.

- [x] **4.2 Implement NFA to DFA Conversion:**
    - [x] Design and implement a robust NFA to DFA conversion algorithm in `compiler/fsa_converter.py`.
    - [x] Ensure proper handling of epsilon transitions.
    - [x] Add comprehensive unit tests in `tests/test_fsa_converter.py`.

- [x] **4.3 Implement DFA Minimization:**
    - [x] Design and implement a DFA minimization algorithm (e.g., Hopcroft's algorithm or Brzozowski's algorithm) in `compiler/fsa_minimizer.py`.
    - [x] Add comprehensive unit tests in `tests/test_fsa_minimizer.py`.

- [x] **4.4 Integrate into CLI:**
    - [x] Update `main.py` to add new options for converting Regex to DFA and minimizing a DFA.
    - [x] Ensure user-friendly display of results.
- [ ] **Real-time DFA Visualization:**
    - [ ] Implement real-time visualization of DFAs (WIP).

- [x] **4.5 Implement NFA/DFA to Regex Conversion:**
    - [x] Create `compiler/fsa_to_regex.py` and implement the state elimination method.
    - [x] Add unit tests in `tests/test_fsa_to_regex.py`.
    - [x] Implement advanced simplification rules to make the generated regular expressions significantly more readable and practical for re-conversion.

- [x] **4.6 Refactor and Improve:**
    - [x] Review all newly integrated code for adherence to `PyCompilerDesign`'s coding style, type hinting, and documentation standards.
    - [x] Optimize performance where necessary.

## Phase 5: Parser Adaptation - COMPLETED

- [x] **Adapt Parser to CppLexer Output:**
    - [x] Modify `compiler/parser.py` to correctly process the new `TokenType` enum and `Token` structure produced by `CppLexer`.
    - [x] Update parsing logic to handle C++ specific syntax elements as needed.
    - [x] Ensure compatibility with the existing AST node structure or extend it as necessary.
    - [x] Write or update unit tests for the parser to validate its functionality with C++ code.
