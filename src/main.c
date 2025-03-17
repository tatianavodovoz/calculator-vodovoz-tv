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

    int isFloatMode = 0;
    if (strcmp(argv[1], "float") == 0) {
        isFloatMode = 1;
    } else if (strcmp(argv[1], "int") != 0) {
        fprintf(stderr, "Invalid mode. Use 'float' or 'int'.\n");
        return 1;
    }

    char* expression = argv[2];
    int lastWasOperator = 1;
    int openBrackets = 0;

    // Validation loop
    for (char* p = expression; *p; p++) {
        if (isspace(*p))
            continue;

        if (isdigit(*p)) {
            lastWasOperator = 0;
            while (isdigit(*p))
                p++;
            if (*p == '.' && !isFloatMode) {
                fprintf(stderr, "Error: Floating point in integer mode\n");
                return 1;
            }
            p--;
        } else if (*p == '(') {
            openBrackets++;
            lastWasOperator = 1;
        } else if (*p == ')') {
            if (openBrackets <= 0) {
                fprintf(stderr, "Error: Mismatched parentheses\n");
                return 1;
            }
            openBrackets--;
            lastWasOperator = 0;
        } else if (strchr("+-*/", *p)) {
            if (lastWasOperator) {
                fprintf(stderr, "Error: Consecutive operators\n");
                return 1;
            }
            lastWasOperator = 1;
        } else {
            fprintf(stderr, "Error: Invalid character\n");
            return 1;
        }
    }

    if (openBrackets != 0 || lastWasOperator) {
        fprintf(stderr, "Error: Invalid expression format\n");
        return 1;
    }

    // Initialize stacks
    IntStack intValues, intOps;
    FloatStack floatValues;
    initIntStack(&intValues);
    initIntStack(&intOps);
    initFloatStack(&floatValues);

    // Main processing loop
    for (char* p = expression; *p; p++) {
        if (isspace(*p))
            continue;

        if (isdigit(*p)) {
            if (isFloatMode) {
                float num = 0;
                int decimal = 0;
                float divisor = 1.0000f;

                while (isdigit(*p) || *p == '.') {
                    if (*p == '.') {
                        decimal = 1;
                    } else {
                        if (decimal) {
                            divisor *= 10.0f;
                            num = num + (*p - '0') / divisor;
                        } else {
                            num = num * 10 + (*p - '0');
                        }
                    }
                    p++;
                }
                p--;
                floatPush(&floatValues, num);
            } else {
                int num = 0;
                while (isdigit(*p)) {
                    num = num * 10 + (*p - '0');
                    p++;
                }
                p--;
                intPush(&intValues, num);
            }
        } else if (*p == '(') {
            intPush(&intOps, *p);
        } else if (*p == ')') {
            while (!isIntEmpty(&intOps) && intPeek(&intOps) != '(') {
                if (isFloatMode)
                    evaluateFloat(&floatValues, &intOps);
                else
                    evaluateInt(&intValues, &intOps);
            }
            intPop(&intOps); // Remove '('
        } else { // Operator
            while (!isIntEmpty(&intOps) && precedence(intPeek(&intOps)) >= precedence(*p)) {
                if (isFloatMode)
                    evaluateFloat(&floatValues, &intOps);
                else
                    evaluateInt(&intValues, &intOps);
            }
            intPush(&intOps, *p);
        }
    }

    // Final evaluation
    while (!isIntEmpty(&intOps)) {
        if (isFloatMode)
            evaluateFloat(&floatValues, &intOps);
        else
            evaluateInt(&intValues, &intOps);
    }

    // Output result
    if (isFloatMode) {
        printf("%.4f\n", floatPeek(&floatValues));
    } else {
        printf("%d\n", intPeek(&intValues));
    }

    return 0;
}
#endif
