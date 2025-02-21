# calculator-vodovoz-tv

## Description

This project is a simple calculator program written in C. It reads an arithmetic expression from standard input, parses
it, and prints the result. The program supports the following operators on integers: `+`, `-`, `*`, `/`, `(`, and `)`.


## Functionality

- Support for integer numbers.
- Handling of basic arithmetic operations: +, -, *, /.
- Support for parentheses to manage the order of operations.
- Ignoring spaces in the expression.

## Program Structure

The program consists of the following main components:

- **Stack**: Implemented using the Stack structure, which stores elements and tracks the top element of the stack.
- **Stack Initialization**: The initStack function initializes the stack.
- **Basic Stack Operations**: Functions push, pop, peek, isFull, and isEmpty for stack manipulation.
- **Operator Precedence**: The precedence function determines the precedence of operators.
- **Executing Operations**: The applyOp function performs arithmetic operations.
- **Expression Processing**: The main logic for processing the expression is implemented in the main function, which reads input, parses it, and computes the result.

## How to Use

1. Compile the program using a C compiler, such as GCC: **gcc main.c -o calc.exe**
2. Run the program: **./main**
3. Enter a mathematical expression and press Enter. The program will output the result of the calculation.

### Example Usage

**Input: (2 + 3) * 4 - 5**
**Output: 15**
