#include <gtest/gtest.h>

extern "C" {
#include "../../src/calculator.h"
}

TEST(StackTest, IntStackPushPop)
{
    IntStack s;
    initIntStack(&s);
    intPush(&s, 10);
    intPush(&s, 20);
    EXPECT_EQ(intPop(&s), 20);
    EXPECT_EQ(intPop(&s), 10);
}

TEST(StackTest, FloatStackPushPop)
{
    FloatStack s;
    initFloatStack(&s);
    floatPush(&s, 10.5);
    floatPush(&s, 20.5);
    EXPECT_DOUBLE_EQ(floatPop(&s), 20.5);
    EXPECT_DOUBLE_EQ(floatPop(&s), 10.5);
}

TEST(StackTest, IntStackIsEmpty)
{
    IntStack s;
    initIntStack(&s);
    EXPECT_TRUE(isIntEmpty(&s));
    intPush(&s, 1);
    EXPECT_FALSE(isIntEmpty(&s));
}

TEST(StackTest, FloatStackIsEmpty)
{
    FloatStack s;
    initFloatStack(&s);
    EXPECT_TRUE(isFloatEmpty(&s));
    floatPush(&s, 1.0);
    EXPECT_FALSE(isFloatEmpty(&s));
}

TEST(StackTest, IntStackOverflow)
{
    IntStack s;
    initIntStack(&s);
    for (int i = 0; i < MAX; i++) {
        intPush(&s, i);
    }
    EXPECT_TRUE(isIntFull(&s)); // Проверяем, что стек полон
    intPush(&s, 100); // Попытка добавить элемент в полный стек
    EXPECT_EQ(intPop(&s), MAX - 1); // Проверяем, что последний элемент все еще в стеке
}

TEST(StackTest, FloatStackOverflow)
{
    FloatStack s;
    initFloatStack(&s);
    for (int i = 0; i < MAX; i++) {
        floatPush(&s, (double)i);
    }
    EXPECT_TRUE(isFloatFull(&s)); // Проверяем, что стек полон
    floatPush(&s, 100.0); // Попытка добавить элемент в полный стек
    EXPECT_DOUBLE_EQ(floatPop(&s), MAX - 1); // Проверяем, что последний элемент все еще в стеке
}

TEST(OperatorTest, ApplyIntOp)
{
    EXPECT_EQ(applyIntOp(10, 5, '+'), 15);
    EXPECT_EQ(applyIntOp(10, 5, '-'), 5);
    EXPECT_EQ(applyIntOp(10, 5, '*'), 50);
    EXPECT_EQ(applyIntOp(10, 5, '/'), 2);

    // Проверка деления на ноль
    EXPECT_EXIT(applyIntOp(10, 0, '/'), ::testing::ExitedWithCode(1), "Error: Division by zero");
}

TEST(OperatorTest, ApplyFloatOp)
{
    EXPECT_DOUBLE_EQ(applyFloatOp(10.5, 5.5, '+'), 16.0);
    EXPECT_DOUBLE_EQ(applyFloatOp(10.5, 5.5, '-'), 5.0);
    EXPECT_DOUBLE_EQ(applyFloatOp(10.5, 5.5, '*'), 57.75);
    EXPECT_DOUBLE_EQ(applyFloatOp(10.5, 5.5, '/'), 1.90909);

    // Проверка деления на ноль
    EXPECT_EXIT(applyFloatOp(10.5, 0.0, '/'), ::testing::ExitedWithCode(1), "Error: Division by zero");
}

TEST(PrecedenceTest, PrecedenceCheck)
{
    EXPECT_EQ(precedence('+'), 1);
    EXPECT_EQ(precedence('-'), 1);
    EXPECT_EQ(precedence('*'), 2);
    EXPECT_EQ(precedence('/'), 2);
    EXPECT_EQ(precedence('^'), 0);
}

TEST(EvaluateTest, EvaluateInt)
{
    IntStack values;
    IntStack ops;
    initIntStack(&values);
    initIntStack(&ops);
    intPush(&values, 3);
    intPush(&values, 4);
    intPush(&ops, '+');
    evaluateInt(&values, &ops);
    EXPECT_EQ(intPop(&values), 7);
}

TEST(EvaluateTest, EvaluateIntEmptyStack)
{
    IntStack values;
    IntStack ops;
    initIntStack(&values);
    initIntStack(&ops);
    EXPECT_EXIT(evaluateInt(&values, &ops), ::testing::ExitedWithCode(1), "Error: Empty stack");
}
