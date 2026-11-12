<h1 align="center" id="title">🐁🐈 Phunter</h1>

<p align="center">
	<img src='assets/logo.png' height="200"/>
</p>

[![python version](https://img.shields.io/badge/Python-3.10%2B-brightgreen)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/License-GNU-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.fr.html)

# **😇 About Phunter**
**Phunter is a tool a very useful tool for finding information about a phone number**

**The hunting cat is able to find :**
- operator
- possible(s) location(s)
- line type 
- reputation
- various scraped information
- spammer or not
- connect to amazon or not
- owner


## **📦 Installation**

- [Python 3](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

```
$ git clone https://github.com/N0rz3/Phunter.git
$ cd ./Phunter
$ pip3 install -r requirements.txt
```

## **🎲 Usage**

```
usage: phunter.py [-h] [-t [TARGET]] [-a [AMAZON]] [-p [PERSON]] [-f [FILE]] [-v] [-o [OUTPUT]]

options:
  -h, --help            show this help message and exit
  -t [TARGET], --target [TARGET]
                        get info by phone number
  -a [AMAZON], --amazon [AMAZON]
                        get confirmation whether Amazon linked by phone number
  -p [PERSON], --person [PERSON]
                        get owner of phone number with inversed annual (Page Blanche)
  -f [FILE], --file [FILE]
                        get info by a file containing phone numbers
  -v, --verify          check your version, update(s), services...
  -o [OUTPUT], --output [OUTPUT]
                        give a file to save the output (only with args: --amazon/-a , --person/-p)
```

### Example usages:

- `$ python3 phunter.py -t +33666666666` or with file `$ python3 phunter.py -f file.txt`

- `$ python3 phunter.py -a +33666666666` or with output `$ python3 phunter.py -a +33666666666 -o output.txt`

### Example results:
![](assets/example.png)


**🛑 With option `-p` you will have to accept the conditions and refuse the notifications, you must be present when this option is executed**

## 🌞 More

### **🗿 Contributions**
Make a [pull requests](https://github.com/N0rz3/Phunter/pulls) with all the details needed to contribute

### **✔️ / ❌ Rules**

**this tool was designed for educational purposes only and is not intended for any mischievous use, I am not responsible for its use.**

### **📜 License**

**This project is [License GPL v3](https://www.gnu.org/licenses/gpl-3.0.fr.html) be sure to follow all rules 👍**

### **💖 Thanks**
- If you like what i do please subscribe 💖. And if you find this tool is useful don't forget to star 🌟

**💶 Support me 👇**

<a href="https://www.buymeacoffee.com/norze" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50" ></a> 

---

# Phunter – Team Xirus Edition

This repository contains a Team Xirus maintenance/audit edition of **Phunter**, originally created by **N0rz3**.

- Upstream project: https://github.com/N0rz3/Phunter
- Original author: N0rz3
- Upstream license: GNU General Public License v3.0 (see `LICENSE`)
- Current upstream version metadata: `0.0.3` (see `config.json`)

## Team Xirus maintenance notes

This edition includes defensive improvements to HTTP request handling, phone-number lookup flow, spam/reputation result handling, and the `--verify` checks. The `verify` tests use mocked HTTP responses; they do not perform live lookups or contact external OSINT services.

## Installation

Use Python 3.10 or newer. Create an isolated virtual environment before installing dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run:

```bash
python phunter.py --help
```

Run the local verification tests:

```bash
python -m unittest discover -s tests -v
```

## Responsible use and privacy

Use Phunter only for lawful, authorized purposes. A phone number is personal data in many contexts: do not investigate people without a legitimate basis, do not publish personal information, and comply with applicable privacy and data-protection laws. Results from third-party sources may be incomplete, outdated, or incorrect.

This Team Xirus edition is an independent maintenance fork; it is not an official release by the original author.
