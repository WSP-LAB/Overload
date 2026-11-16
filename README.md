# Overloading Ad Blockers: Exploiting Filtering Logic for Selective Denial of Service

This repository contains scripts for executing three variants of the Overload
attack. Given a list of input HTML files, each attack script generates
corresponding adversarial HTML elements, injects them into the original HTML
files, and saves the resulting adversarial pages.

For Attack I, we additionally provide keyword sets extracted from EasyList,
located in the `utils/keywordlist` directory.

We also provide two demonstration videos at this
[link](https://drive.google.com/drive/folders/1FMyYs9HE0TRsSOCfwI40pERfLcRH7xfW?usp=sharing).
These videos illustrate Attack I using greedy and random sampling strategies,
respectively. In both demonstrations, the attack is evaluated against AdBlocker
Ultimate installed on Firefox, which exhibited the largest page load times in
our main experiment.

## Project Structure

```
.
├── overload_attack_injection_1_GS.py   # Attack 1: Greedy Sampling
├── overload_attack_injection_1_RS.py   # Attack 1: Random Sampling
├── overload_attack_injection_2.py      # Attack 2
├── overload_attack_injection_3.py      # Attack 3
├── requirements.txt
├── websites/                           # Directory containing input HTML files
├── websites.txt                        # List of HTML filenames to process
├── utils/
│   ├── attack.py                       # URL generator for Attack I
│   ├── js_injector.py                  # Adversarial HTML tag generator
│   ├── util.py                         # Common utilities for file I/O and tag injection
│   └── keywordlist/                    # Keyword sets
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare HTML Pages

- Place all target `.html` files in the `websites/` directory.
- Create a `websites.txt` file that lists the names of the HTML files to
  process, one per line.

Example `websites.txt`:
```
ccs2026a_hotcrp_com.html
```

## Running the Attacks

Each of the following scripts injects adversarial HTML elements into the
specified HTML pages using a different attack variant:

```bash
python overload_attack_injection_1_GS.py websites.txt  # Attack 1: Greedy Sampling
python overload_attack_injection_1_RS.py websites.txt  # Attack 1: Random Sampling

python overload_attack_injection_2.py websites.txt     # Attack 2
python overload_attack_injection_3.py websites.txt     # Attack 3
```

The generated adversarial HTML files are saved to the `websites/` directory.


---

For any questions, please contact the authors.
