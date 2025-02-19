#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

#define MAX 1024

typedef struct 
{
    int top;
    int items[MAX];
} Stack;

void initStack(Stack *s) 
{
    s->top = -1;
}

int isFull(Stack *s) 
{
    return s->top == MAX - 1;
}

int isEmpty(Stack *s) 
{
    return s->top == -1;
}

void push(Stack *s, int item) 
{
    if (!isFull(s)) 
    {
        s->items[++(s->top)] = item;
    }
}

int pop(Stack *s) 
{
    if (!isEmpty(s)) 
    {
        return s->items[(s->top)--];
    }
    return 0; 
}

int peek(Stack *s) 
{
    if (!isEmpty(s)) 
    {
        return s->items[s->top];
    }
    return 0; 
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

int applyOp(int a, int b, char op) 
{
    switch (op) 
    {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/': return a / b; 
    }
    return 0; 
}

void evaluate(Stack *values, Stack *ops) 
{
    int b = pop(values);
    int a = pop(values);
    char op = pop(ops);
    push(values, applyOp(a, b, op));
}

void processOperator(Stack *values, Stack *ops) 
{
    while (!isEmpty(ops) && precedence(peek(ops)) >= precedence(peek(ops))) 
    {
        evaluate(values, ops);
    }
}

int main() 
{
    char expression[MAX];
    fgets(expression, MAX, stdin);

    Stack values, ops;
    initStack(&values);
    initStack(&ops);

    for (char *p = expression; *p; p++) 
    {
        if (isspace(*p)) continue; // Skip whitespace

        if (isdigit(*p)) 
        {
            int num = 0;
            while (isdigit(*p)) 
            {
                num = num * 10 + (*p - '0');
                p++;
            }
            push(&values, num);
            p--; // Adjust for the loop increment
        } 
        
        else if (*p == '(') 
        {
            push(&ops, *p);
        } 
        
        else if (*p == ')') 
        {
            while (!isEmpty(&ops) && peek(&ops) != '(') 
            {
                evaluate(&values, &ops);
            }
            pop(&ops); // Remove ( from stack
        } 
        
        else 
        {   // Operator
            while (!isEmpty(&ops) && precedence(peek(&ops)) >= precedence(*p)) 
            {
                evaluate(&values, &ops);
            }
            push(&ops, *p);
        }
    }

    while (!isEmpty(&ops)) 
    {
        evaluate(&values, &ops);
    }

    printf("%d\n", pop(&values));
    return 0;
}

