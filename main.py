from compiler.lexer.lexer import CppLexer
from compiler.lexer.token import TokenType
from compiler.utils.token_classifier import TokenClassifier
import sys

def print_tokens(tokens: list, max_tokens: int = 50) -> None:
    """Print tokens in a formatted way"""
    print(f"{'Type':<25} {'Value':<20} {'Line':<6} {'Column':<6}")
    print("-" * 60)
    
    for i, token in enumerate(tokens[:max_tokens]):
        value_display = repr(token.value) if token.value else 'EOF'
        if len(value_display) > 18:
            value_display = value_display[:15] + "..."
        
        print(f"{token.type.name:<25} {value_display:<20} {token.line:<6} {token.column:<6}")
    
    if len(tokens) > max_tokens:
        print(f"... and {len(tokens) - max_tokens} more tokens")


if __name__ == "__main__":
    sample_code = '''
    #include <iostream>
    #include <string>
    
    class Calculator {
    private:
        int result;
        
    public:
        Calculator() : result(0) {}
        
        int add(int a, int b) {
            return a + b;
        }
        
        void display() {
            cout << "Result: " << result << endl;
        }
    };
    
    int main() {
        Calculator calc;
        int x = 10, y = 20;
        
        // This is a comment
        int sum = calc.add(x, y);
        
        /* Multi-line
           comment */
        
        if (sum > 25) {
            cout << "Sum is greater than 25" << endl;
        }
        
        return 0;
    }
    '''
    
    choice = input("Enter '1' to use sample code, or '2' to enter your own code: ")
    
    code_to_lex = ""
    if choice == '1':
        code_to_lex = sample_code
    elif choice == '2':
        print("Enter your C++ code and press Ctrl+D (Unix) or Ctrl+Z then Enter (Windows) to finish:")
        code_to_lex = sys.stdin.read()
    else:
        print("Invalid choice. Using sample code.")
        code_to_lex = sample_code

    lexer = CppLexer(code_to_lex)
    tokens = lexer.tokenize_and_filter(include_comments=True, include_newlines=True)

    classifier = TokenClassifier(lexer.keywords)

    for token in tokens:
        token_class = classifier.classify_token(token)
        token_value = token.value.strip() or "NEWLINE"
        print(f"<{token_class} , {token_value}>")