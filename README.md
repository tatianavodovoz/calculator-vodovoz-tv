# calculator-vodovoz-tv

## What Has Been Done
This project is a simple server application written in Python. It allows users to interact with a calculator through HTTP requests. The server processes arithmetic expressions and returns the calculated results. The application supports the following operators on integers: `+`, `-`, `*`, `/`, `(`, and `)`. The server reads input from the user, processes the expression, and outputs the calculated result.

## How to Run/Use It

To run the server, navigate to the project directory in your terminal:

```bash
   cd ~/calculator-vodovoz-tv
```
To start the server, use the following command:

```bash
   python3 server.py
```

To enable JSON logging, run the server with the following command:

```bash
   python3 server.py --json-logs
```

To send a calculation request to the server, use the following command:
```bash
   curl -X POST http://localhost:8000/calc -H "Content-Type: application/json" -d '"2 + 2 * 2"'
```
Result:
```bash
   "6"
```

## How It's Made

The server consists of the following main components:

- Server Setup: The server is implemented in server.py, which sets up a basic HTTP server listening on a specified port.
- Request Handling: The server processes incoming requests and returns responses based on the results of the calculator.
- Calculator Interaction: The server interacts with a calculator program, handling return codes and results.
- Error Handling: The server manages various scenarios, including timeouts and error messages.
- Logging: The server uses structlog for logging events, providing formatted logs in the console and JSON format.

## Daily Task Report - server

### DZTVP-4 (07/03/2025)
**Task**: 
Set up the development environment for the Python server.
**Results**: 
Successfully installed Python and verified that all necessary libraries (e.g., `json`, `subprocess`) are available. The development environment is now fully prepared for further development.

### DZTVP-5(07/03/2025)
**Task**: 
Create the basic structure of the server.
**Results**: 
Created the `server.py` file and set up a basic HTTP server that listens on the specified port. Implemented a handler for the root URL, which successfully returns "Hello, World!" when accessed. The server structure is now in place for handling requests.

### DZTVP-6 (08/03/2025)
**Task**: 
Implement interaction with the calculator.
**Results**: 
Developed a function to run the calculator and handle its results effectively. The function manages return codes as follows:
  - Successfully retrieves the result when the return code is 0.
  - Returns an appropriate error message when the return code is not 0.
  - Provides a message indicating that the result was not obtained if the return code is 0 but the result is missing.
  - Implemented timeout handling for the calculator execution, ensuring that errors are returned if the execution exceeds the specified time limit.

### DZTVP-7 (08/03/2025)
**Task**: 
Implement server response generation based on calculator results.
**Results**: 
The server now generates responses based on the results from the calculator:
  - Returns a response with code 200 and the result if the request is valid and the calculator returns a result.
  - Returns a response with code 500 and an error message if the request is valid but the calculator returns an error.
  - Returns a response with code 200 if the request is valid but the result is missing. This ensures clear communication of the server's status to the client.

### DZTVP-8 (08/03/2025)
**Task**:
Implement logging using `structlog`.
**Results**: 
Successfully set up a logging system for the Python server using the `structlog` library. The logging is organized and formatted for clarity, including:
  - Informative logs that are easy to read, with timestamps, log levels, and messages.
  - Implementation of JSON logging for easier monitoring and analysis, enhancing the server's observability and debugging capabilities.
  
## Daily Task Report - gui

### DZTVP-11 (19/03/2025)
**Task**: 
Implement a mathematical expression validator. 
**Results**: 
Successfully created the `MathExpressionValidator` class to check the validity of input mathematical expressions. The implementation includes:
  - Validation of allowed characters to ensure only valid symbols are processed.
  - Checking for balanced parentheses to prevent syntax errors in expressions.

### DZTVP-12 (19/03/2025)
**Task**: 
Create a class for handling calculations in a separate thread. 
**Results**:
Implemented the `CalculationWorker` class to perform calculations in a separate thread. The class effectively handles:
  - Successful and error responses from the server, ensuring smooth communication between threads.
  - Use of signals to transmit data back to the main thread, enhancing the responsiveness of the application.

### DZTVP-13 (19/03/2025)
**Task**: 
Develop the main application window. 
**Results**: 
Created the `CalculatorClient` class to represent the main application window. The implementation includes:
  - A user-friendly interface with controls for inputting expressions, buttons for operations, and displays for results and error messages.
  - Event handling for buttons and other controls, ensuring a responsive and interactive user experience.
  
![Finite State Machine](finite_state_machine_calc.jpg)

## Finite State Machine for Calculator

### States
- **Initial State**: The initial state when the application is ready for input.
- **Validating Expression**: The state where the application checks the entered mathematical expression.
- **Error State**: The state where the application displays an error message.
- **Sending Request to Server**: The state where the application sends a request to the server for calculation.
- **Displaying Result**: The state where the application displays the result of the calculation.

### Transitions
**Initial State**:
User enters expression → Transition to Validating Expression state.

**Validating Expression**:
Valid → Transition to Sending Request to Server state.
Invalid → Transition to Error State.

**Error State**:
User corrects input → Transition back to Initial State.

**Sending Request to Server**:
Success → Transition to Displaying Result state.
Error → Transition to Error State.

**Displaying Result**:
User requests new calculation → Transition back to Initial State.

