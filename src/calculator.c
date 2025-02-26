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
                exit(EXIT_FAILURE);
            }
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

