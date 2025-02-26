#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include "calculator.h"

void initIntStack(IntStack *s) 
{
    s->top = -1;
}

void initFloatStack(FloatStack *s) 
{
    s->top = -1;
}

int isIntFull(IntStack *s) 
{
    return s->top == MAX - 1;
}

int isFloatFull(FloatStack *s) 
{
    return s->top == MAX - 1;
}

int isIntEmpty(IntStack *s) 
{
    return s->top == -1;
}

int isFloatEmpty(FloatStack *s) 
{
    return s->top == -1;
}

void intPush(IntStack *s, int item) 
{
    if (!isIntFull(s)) 
    {
        s->items[++(s->top)] = item;
    }
}

void floatPush(FloatStack *s, double item) 
{
    if (!isFloatFull(s)) 
    {
        s->items[++(s->top)] = item;
    }
}

int intPop(IntStack *s) 
{
    if (!isIntEmpty(s)) 
    {
        return s->items[(s->top)--];
    }
    return 0; 
}

double floatPop(FloatStack *s) 
{
    if (!isFloatEmpty(s)) 
    {
        return s->items[(s->top)--];
    }
    return 0.0; 
}

int intPeek(IntStack *s) 
{
    if (!isIntEmpty(s)) 
    {
        return s->items[s->top];
    }
    return 0; 
}

double floatPeek(FloatStack *s) 
{
    if (!isFloatEmpty(s)) 
    {
        return s->items[s->top];
    }
    return 0.0; 
}

int precedence(char op) 
{
    switch (op) 
    {
        case '+':
        case '-': return 1;
        case '*':
        case '/': return 2;
        default: return 0;
    }
}

int applyIntOp(int a, int b, char op) 
{
    switch (op) 
    {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/':
            if (b == 0) 
            {
                fprintf(stderr, "Error: Division by zero\n");
                exit(EXIT_FAILURE }
            return a / b; 
    }
    return 0; 
}

double applyFloatOp(double a, double b, char op) 
{
    switch (op) 
    {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/':
            if (b == 0.0) 
            {
                fprintf(stderr, "Error: Division by zero\n");
                exit(EXIT_FAILURE);
            }
            return a / b; 
    }
    return 0.0; 
}

void evaluateInt(IntStack *values, IntStack *ops) 
{
    int b = intPop(values);
    int a = intPop(values);
    char op = intPop(ops);
    intPush(values, applyIntOp(a, b, op));
}

void evaluateFloat(FloatStack *values, IntStack *ops) 
{
    double b = floatPop(values);
    double a = floatPop(values);
    char op = intPop(ops);
    floatPush(values, applyFloatOp(a, b, op));
}

void processOperator(IntStack *values, IntStack *ops) 
{
    while (!isIntEmpty(ops) && precedence(intPeek(ops)) >= precedence(intPeek(ops))) 
    {
        evaluateInt(values, ops);
    }
}

int main(int argc, char *argv[]) 
{
    if (argc < 2) 
    {
        fprintf(stderr, "Usage: %s <mode>\n", argv[0]);
        return 1;
    }

    int isFloatMode = 0;

    if (strcmp(argv[1], "float") == 0) 
    {
        isFloatMode = 1;
    } 
    else if (strcmp(argv[1], "int") != 0) 
    {
        fprintf(stderr, "Invalid mode. Use 'float' or 'int'.\n");
        return 1;
    }
    
    char expression[MAX];
    fgets(expression, MAX, stdin);

    for (char *p = expression; *p; p++) 
    {
        if (!isdigit(*p) && !strchr("()*+/- \n", *p)) 
        {
            fprintf(stderr, "Error: Invalid character\n");
            return 1;
        }
    }

    IntStack intValues;
    IntStack intOps;
    FloatStack floatValues;
    
    initIntStack(&intValues);
    initIntStack(&intOps);
    initFloatStack(&floatValues);

    for (char *p = expression; *p; p++) 
    {
        if (isspace(*p)) continue;

        if (isdigit(*p) || (*p == '.')) 
        {
            if (isFloatMode) 
            {
                double num = 0.0;
                double decimalPlace = 1.0;
                int isDecimal = 0;

                while (isdigit(*p) || (*p == '.' && !isDecimal)) 
                {
                    if (*p == '.') 
                    {
                        isDecimal = 1;
                    } 
                    else 
                    {
                        num = num * 10 + (*p - '0');
                        if (isDecimal) 
                        {
                            decimalPlace *= 10.0;
                        }
                    }
                    p++;
                }
                if (isDecimal) 
                {
                    num /= decimalPlace;
                }
                floatPush(&floatValues, num);
                p--;
            } 
            else 
            {
                int num = 0;
                while (isdigit(*p)) 
                {
                    num = num * 10 + (*p - '0');
                    p++;
                }
                intPush(&intValues, num);
                p--;
            }
        } 
        else if (*p == '(') 
        {
            intPush(&intOps, *p);
        } 
        else if (*p == ')') 
        {
            while (!isIntEmpty(&intOps) && intOps.items[intOps.top] != '(') 
            {
                if (isFloatMode) evaluateFloat(&floatValues, &intOps);
                else evaluateInt(&intValues, &intOps);
            }
            intPop(&intOps);
        } 
        else 
        {
            while (!isIntEmpty(&intOps) && precedence(intPeek(&intOps)) >= precedence(*p)) 
            {
                if (isFloatMode) evaluateFloat(&floatValues, &intOps);
                else evaluateInt(&intValues, &intOps);
            }
            intPush(&intOps, *p);
        }
    }

    while (!isIntEmpty(&intOps)) 
    {
        if (isFloatMode) evaluateFloat(&floatValues, &intOps);
        else evaluateInt(&intValues, &intOps);
    }

    if (isFloatMode) 
    {
        printf("%.5f\n", float Pop(&floatValues));
    } 
    else 
    {
        printf("%d\n", intPop(&intValues));
    }
    
    return 0;
}
