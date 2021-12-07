# Description
soil or Stack Oriented Interpreted Language
is a project of mine that I did in python 
to challenge myself to dive into the world of 
language design despite my 0 knowledge in the field.

# How to run the script
You can run soil scripts from terminal and type the following command:

```
    soil [filename]
```

example:

```
    soil test.sl
```

remember that the soil interpreter can accept any kind of file extension, it could even be .txt, but it's recommended to use the .sl extension just for naming convention.

# Basic Syntax and Tutorial
soil's syntax is a mix between assembly and python's bytecode
with the usual format of **[opname] [arg1] [arg2]** and so on....

* ### Hello World in soil

```
    print "Hello World"
```

* ### Variables
To create a variable in soil, you have to load two things onto the stack: **the value**,
and **the name of the variable**. and then after that you can spawn a variable.

```
    load int 5      # load the value 5 onto the stack
    load string x   # load the name of the variable (no quotes needed if the string has no spaces)
    spawn var       # spawn the variable
```

and now we have a variable called "x" with the value of 5. and now we can print the variable:

```
    print var x
```

to reassign value to a variable, you can load a value onto the stack and then
use the keyword `assign` and then followed
by the variable name:

```
    load int 10
    assign x
```

and now the variable "x" contains the number 10.

# Arithmetic Operations

| OPERATOR 	| Description                                                          	|
|----------	|----------------------------------------------------------------------	|
| add      	| add two numbers previously loaded on the stack                       	|
| sub      	| subtract two numbers previously loaded onto the stack                	|
| mul      	| multiply two numbers previously loaded onto the stack                	|
| div      	| perform division on the two numbers previously loaded onto the stack 	|
| mod      	| perform modulo on the two numbers previously loaded onto the stack   	|

Arithmetic operations can be done in soil by
1. Loading the first operand
2. Loading the second operand
3. And then perform arithmetic operations on those two numbers

Like this:

```
    load int 10
    load int 5
    add inplace
```

storing the result of the arithmetic operation can be done in two ways: either store them inplace, 
or adjacent to the loaded operands. Let's visualize the stack!

```
    load int 10
```

**stack: [10]**

```
    load int 5
```

**stack: [10, 5]**

if you use the inplace mode, it will pop the two operands, add them, and then push result
onto the stack:

```
    add inplace
```

**stack: [15]**

if you use adjacent mode, it will copy the two operands, add them, and then push the result
onto the stack:

```
    add adjacent
```

**stack: [10, 5, 15]**