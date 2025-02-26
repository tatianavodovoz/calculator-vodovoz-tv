#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#define MAX 1024

typedef struct 
{
    int top;
    int items[MAX];
} IntStack;

typedef struct 
{
    int top;
    double items[MAX];
} FloatStack;

// Объявления функций
void initIntStack(IntStack* s);
void intPush(IntStack* s, int value);
int intPop(IntStack* s);
int isIntEmpty(IntStack* s);
int isIntFull(IntStack *s);
int intPeek(IntStack *s);

void initFloatStack(FloatStack* s);
void floatPush(FloatStack* s, double value);
double floatPop(FloatStack* s);
int isFloatEmpty(FloatStack* s);
int isFloatFull(FloatStack *s);
double floatPeek(FloatStack *s);

int applyIntOp(int a, int b, char op);
double applyFloatOp(double a, double b, char op);

int precedence(char op);

void evaluateInt(IntStack* values, IntStack* ops);
void evaluateFloat(FloatStack *values, IntStack *ops);
void processOperator(IntStack *values, IntStack *ops);

