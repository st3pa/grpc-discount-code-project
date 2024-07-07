# Python GRPC Discount Code Project

This Project aim to introduce grpc into discount code management/

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```

## Usage

```python
#Run the server
python server.py

#Run the client
#Generate codes
python clients.py generate --count <count> --length <length>

#Use Code
python clients.py use --code <code>
```
## Test
```bash
#Run Tests
python -m unittest discover
```

## Troubleshoot
```bash
#Run Tests
#If discounts.db is not found inside db-files and 
#its not generated automatically when server server starts
#Run this
python db-files/setup_db.py
```