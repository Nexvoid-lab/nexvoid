# Nexvoid v1.0

A modern systems programming language designed for scripting, cybersecurity, and automation.

## Features

- **Object-Oriented Programming** - Classes, protocols, inheritance
- **Type Hints** - Optional type annotations for safety
- **Decorators** - @validate, @secure, @audit for enforcing behavior
- **List Comprehensions** - `map expr from x in arr where condition`
- **String Interpolation** - `"Hello {name}!"`
- **Protocol/Interfaces** - Type contracts for classes

## Installation

```bash
pip install nexvoid


### v2.0 (Coming Soon) 🚀
- **GUI Framework** - Build desktop & mobile applications
- **Expanded Stdlib** - 30+ quality modules (crypto, networking, AI, data science)
- **Security Tools** - Penetration testing, encryption, auditing
- **Data Science** - NumPy-equivalent arrays, data transformation
- **Web Framework** - HTTP clients, REST APIs

## Vision

Nexvoid is designed to evolve into a **full-featured systems language** supporting:
- Systems programming
- Cybersecurity automation
- Data science pipelines
- Mobile/desktop GUI applications
- Enterprise automation

Stay tuned for v2.0!

## Installation

```bash
pip install nexvoid


#===========================================================================
#==========================================================================
## Quick Start

### Example 1: Simple Greeting (Easiest)

Create `greet.nex`:

```nexvoid
fun hello(name)
    cout("Hello {name}!")

hello("friend")

#run the code like
#nexvoid greet.nex
#output: Hello friend !
#==============================================================
#**************************************************************
#*******EXAMPLE TWO********
#======BANKING SYSTEM======

class Account
    create(owner, balance)
        this.owner = owner
        this.balance = balance
    
    deposit(amount)
        this.balance = this.balance + amount
        cout("{this.owner} deposited {amount}")
    
    show_balance()
        cout("Balance: {this.balance}")

account = Account("Ibra", 1000)
account.deposit(500)
account.show_balance()



#RUN: nexvoid bank(or any file name used).nex






