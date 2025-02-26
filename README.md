# calculator-vodovoz-tv

## What Has Been Done?

This project is a simple calculator application written in C. It allows users to input arithmetic expressions and calculates the result. The program supports the following operators on integers: `+`, `-`, `*`, `/`, `(`, and `)`. The program reads input from the user, processes the expression, and outputs the calculated result.

## How to Run/Use It

You should go to the repository in the terminal:
```bash
   cd ~/calculator-vodovoz-tv
```

### Makefile

```bash
make all            # to build program (app.exe) and unit tests (unit-tests.exe)
make clean          # to clean build artifacts
make run-int        # to run app.exe
make run-float      # to run app.exe --float
make run-unit-test  # to run unit-tests.exe
make format         # to format .cpp .c .h files using WebKit style
```

## How It's Made

The program consists of the following main components:

- Stack: Implemented using the IntStack and FloatStack structures, which store elements and track the top element of the stack.
- Stack Initialization: The initIntStack and initFloatStack functions initialize the respective stacks.
- Basic Stack Operations: Functions intPush, intPop, floatPush, floatPop, intPeek, and floatPeek for stack manipulation.
- Operator Precedence: The precedence function determines the precedence of operators.
- Executing Operations: The applyIntOp and applyFloatOp functions perform arithmetic operations.
- Expression Processing: The main logic for processing the expression is implemented in the main function, which reads input, parses it, and computes the result.
