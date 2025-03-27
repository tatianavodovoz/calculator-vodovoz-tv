CC = gcc
CXX = g++

CFLAGS = -Wall -Wextra -Wpedantic -Werror -std=c11
CXXFLAGS = -Wall -Wextra -Wpedantic -Werror -std=c++17
LDFLAGS = -lstdc++ -lm
TEST_LDFLAGS = -lgtest -lgtest_main -lpthread

SRC_DIR = src
BUILD_DIR = build
UNIT_TESTS_DIR = tests/unit

# Application
APP_SRC = $(SRC_DIR)/main.c $(SRC_DIR)/calculator.c
APP_OBJ = $(BUILD_DIR)/main.o $(BUILD_DIR)/calculator.o
APP_EXE = $(BUILD_DIR)/app.exe

# Unit tests
TEST_SRC = $(UNIT_TESTS_DIR)/tests.cpp $(SRC_DIR)/calculator.c
TEST_OBJ = $(BUILD_DIR)/tests.o $(BUILD_DIR)/calculator.o
TEST_EXE = $(BUILD_DIR)/unit-tests.exe

# GoogleTest files
GTEST_DIR := googletest/googletest
GTEST_SRC_DIR := $(GTEST_DIR)/src
GTEST_HEADERS := $(GTEST_DIR)/include/gtest/*.h $(GTEST_DIR)/include/gtest/internal/*.h
GTEST_BUILD_DIR := $(BUILD_DIR)/gtest
GTEST_ALL_OBJ  := $(GTEST_BUILD_DIR)/gtest-all.o
GTEST_MAIN_OBJ := $(GTEST_BUILD_DIR)/gtest_main.o
GTEST_MAIN_A   := $(GTEST_BUILD_DIR)/gtest_main.a

# Formatting configuration
FORMAT_DIRS = $(SRC_DIR) $(UNIT_TESTS_DIR)
FORMAT_EXTS = *.cpp *.c *.h
CLANG_FORMAT = clang-format

# Python integration tests
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
INT_TEST_DIR = tests/integration
INT_TESTS = $(INT_TEST_DIR)/tests.py

# Python server/client
SERVER_SCRIPT = server.py
CLIENT_SCRIPT = client.py

.PHONY: all clean run-app run-unit-test format venv run-integration-tests run-server run-client

all: $(APP_EXE)

# Build application
$(APP_EXE): $(APP_OBJ)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BUILD_DIR)/main.o: $(SRC_DIR)/main.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD_DIR)/calculator.o: $(SRC_DIR)/calculator.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

# Сборка Google Test
$(GTEST_ALL_OBJ): $(GTEST_SRC_DIR)/gtest-all.cc $(GTEST_HEADERS)
	@echo "Building gtest-all.o"
	@mkdir -p $(GTEST_BUILD_DIR)
	$(CXX) $(CXXFLAGS) -isystem $(GTEST_DIR)/include -I$(GTEST_DIR) -c $< -o $@

$(GTEST_MAIN_OBJ): $(GTEST_SRC_DIR)/gtest_main.cc $(GTEST_HEADERS)
	@echo "Building gtest_main.o"
	@mkdir -p $(GTEST_BUILD_DIR)
	$(CXX) $(CXXFLAGS) -isystem $(GTEST_DIR)/include -I$(GTEST_DIR) -c $< -o $@

$(GTEST_MAIN_A): $(GTEST_ALL_OBJ) $(GTEST_MAIN_OBJ)
	@echo "Archiving gtest_main.a"
	ar rcs $@ $^

# Build unit tests
$(TEST_EXE): $(TEST_OBJ) $(GTEST_MAIN_A)
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(TEST_LDFLAGS) $(LDFLAGS)

$(BUILD_DIR)/tests.o: $(UNIT_TESTS_DIR)/tests.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -rf $(BUILD_DIR)

run-int: $(APP_EXE)
	@$< int

run-float: $(APP_EXE)
	@$< float

run-unit-test: $(TEST_EXE)
	@$<

format:
	@find $(FORMAT_DIRS) -type f \( \
	-name "*.cpp" -o \
	-name "*.c" -o \
	-name "*.h" \
	\) -exec $(CLANG_FORMAT) -i -style=file {} +

$(VENV):requirements.txt
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt

run-integration-tests: $(VENV) $(APP_EXE)
	@. $(VENV)/bin/activate && pytest $(INT_TESTS)

run-server: $(VENV)
	@$(PYTHON) $(SERVER_SCRIPT)

run-client: $(VENV)
	@$(PYTHON) $(CLIENT_SCRIPT)

run-app: $(APP_EXE)
	@echo "Running application..."
	@./$(APP_EXE)
