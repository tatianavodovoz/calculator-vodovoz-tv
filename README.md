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

## Daily Task Report

### DZTVP-4
**Task**: 
Set up the development environment for the Python server.
**Results**: 
Successfully installed Python and verified that all necessary libraries (e.g., `json`, `subprocess`) are available. The development environment is now fully prepared for further development.

### DZTVP-5
**Task**: 
Create the basic structure of the server.
**Results**: 
Created the `server.py` file and set up a basic HTTP server that listens on the specified port. Implemented a handler for the root URL, which successfully returns "Hello, World!" when accessed. The server structure is now in place for handling requests.

### DZTVP-6
**Task**: 
Implement interaction with the calculator.
**Results**: 
Developed a function to run the calculator and handle its results effectively. The function manages return codes as follows:
  - Successfully retrieves the result when the return code is 0.
  - Returns an appropriate error message when the return code is not 0.
  - Provides a message indicating that the result was not obtained if the return code is 0 but the result is missing.
  - Implemented timeout handling for the calculator execution, ensuring that errors are returned if the execution exceeds the specified time limit.

### DZTVP-7
**Task**: 
Implement server response generation based on calculator results.
**Results**: 
The server now generates responses based on the results from the calculator:
  - Returns a response with code 200 and the result if the request is valid and the calculator returns a result.
  - Returns a response with code 500 and an error message if the request is valid but the calculator returns an error.
  - Returns a response with code 200 if the request is valid but the result is missing. This ensures clear communication of the server's status to the client.

### DZTVP-8
**Task**:
Implement logging using `structlog`.
**Results**: 
Successfully set up a logging system for the Python server using the `structlog` library. The logging is organized and formatted for clarity, including:
  - Informative logs that are easy to read, with timestamps, log levels, and messages.
  - Implementation of JSON logging for easier monitoring and analysis, enhancing the server's observability and debugging capabilities.

