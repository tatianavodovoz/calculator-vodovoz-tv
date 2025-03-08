#include "calculator.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef UNIT_TEST
int main(int argc, char* argv[])
{
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <mode> <expression>\n", argv[0]);
        return 1;
    }

    // Определяем режим работы
    if (strcmp(argv[1], "float") == 0) {
        isFloatMode = 1;
    } else if (strcmp(argv[1], "int") != 0) {
        fprintf(stderr, "Invalid mode. Use 'float' or 'int'.\n");
        return 1;
    }

    char* expression = argv[2];

    // Check for valid characters and initial conditions
    int lastWasOperator = 1; // Start with true to allow a number at the start
    int openBrackets = 0;

    for (char* p = expression; *p; p++) {
        if (isspace(*p))
            continue; // Skip whitespace

        if (isdigit(*p)) {
            lastWasOperator = 0; // We found a number
            while (isdigit(*p)) {
                p++;
            }
            if (*p == '.') { // If we encounter a decimal point, it's an error
                fprintf(stderr, "Error: Invalid character - floating point number detected\n");
                return 1;
            }
            p--; // Adjust for the loop increment
        } else if (*p == '(') {
            openBrackets++;
            lastWasOperator = 1; // Reset, as '(' is not an operator
        } else if (*p == ')') {
            if (lastWasOperator) { // If the last was an operator, it's an error
                fprintf(stderr, "Error: Unexpected closing parenthesis\n");
                return 1;
            }
            openBrackets--;
        } else if (strchr("+-*/", *p)) {
            if (lastWasOperator) { // If the last was also an operator, it's an error
                fprintf(stderr, "Error: Two consecutive operators\n");
                return 1;
            }
            lastWasOperator = 1; // We found an operator
        } else {
            fprintf(stderr, "Error: Invalid character\n");
            return 1; // Return code not equal to 0
        }
    }

    if (openBrackets != 0) {
        fprintf(stderr, "Error: Mismatched parentheses\n");
        return 1;
    }

    if (lastWasOperator) { // If the expression ends with an operator, it's an error
        fprintf(stderr, "Error: Expression cannot end with an operator\n");
        return 1;
    }

    IntStack intValues;
    IntStack intOps;
    FloatStack floatValues;

    initIntStack(&intValues);
    initIntStack(&intOps);
    initFloatStack(&floatValues);

    for (char* p = expression; *p; p++) {
        if (isspace(*p))
            continue; // Skip whitespace

        if (isdigit(*p)) {
            if (isFloatMode) {
                fprintf(stderr, "Error: Invalid character - floating point number detected\n");
                return 1; // We can't have floats in float mode
            }
            int num = 0;
            while (isdigit(*p)) {
                num = num * 10 + (*p - '0');
                p++;
            }
            intPush(&intValues, num);
            p--; // Adjust for the loop increment
        } else if (*p == '(') {
            intPush(&intOps, *p);
        } else if (*p == ')') {
            while (!isIntEmpty(&intOps) && intOps.items[intOps.top] != '(') {
                evaluateInt(&intValues, &intOps);
            }
            intPop(&intOps); // Remove '(' from stack
        } else { // Operator
            while (!isIntEmpty(&intOps) && precedence(intPeek(&intOps)) >= precedence(*p)) {
                evaluateInt(&intValues, &intOps);
            }
            intPush(&intOps, *p);
        }
    }

    while (!isIntEmpty(&intOps)) {
        evaluateInt(&intValues, &intOps);
    }

    printf("%d\n", intPop(&intValues));

    return 0;
}
#endif
