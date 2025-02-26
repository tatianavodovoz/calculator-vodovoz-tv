#include "calculator.h"

int main(int argc, char *argv[]) 
{
    if (argc < 2) 
    {
        fprintf(stderr, "Usage: %s <mode>\n", argv[0]);
        return 1;
    }

    int isFloatMode = 0;

    // Определяем режим работы
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

    // Check for valid characters
    for (char *p = expression; *p; p++) 
    {
        if (!isdigit(*p) && !strchr("()*+/- \n", *p)) 
        {
            fprintf(stderr, "Error: Invalid character\n");
            return 1; // Return code not equal to 0
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
        if (isspace(*p)) continue; // Skip whitespace

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
                p--; // Adjust for the loop increment
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
                p--; // Adjust for the loop increment
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
            intPop(&intOps); // Remove '(' from stack
        } 
        else 
        { // Operator
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
        printf("%.5f\n", floatPop(&floatValues));
    } 
    else 
    {
        printf("%d\n", intPop(&intValues));
    }
    
    
    return 0;
}

