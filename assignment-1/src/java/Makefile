JAVAC = javac
JAVA = java
BIN_DIR = bin

all: compile

compile:
	mkdir -p $(BIN_DIR)
	$(JAVAC) -d $(BIN_DIR) MatrixMul.java Verify.java

verify: compile
	$(JAVA) -cp $(BIN_DIR) matrix.Verify

clean:
	rm -rf $(BIN_DIR)

.PHONY: all compile verify clean
