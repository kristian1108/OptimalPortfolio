# OptimalPortfolio
This program collects and analyzes financial data in order to suggest an optimal portfolio given a desired return.

## Setup 
Before you can run the program, you will need to do 3 things: 
1. Install python3 virtual environment. To do this, navigate to the cloned directory in your 
terminal/command prompt and run `python3 -m venv /path/to/new/virtual/environment`. For example, `python3 -m venv venv` will 
create the virtual environment in the current directory and name it `venv`.
2. Activate the virtual environment by running `source venv/bin/activate`. (If you named your virtuanl environment something
other than `venv`, you must replace `venv` with the name of your virtual environment)
3. Install the requirements. `pip install -r requirements.txt`  

## Run 
Simply run the `main.py` file. Example: `python main.py`

Note: if it's your first time running the program, you will have to opt to create a new list when prompted. In any subsequent
use, you have the option to create new lists through the text prompts, or you can simply add the assets you which to 
consider into the `tickers` directory as a `.txt` file. Separate tickers by lines. 

## Threading 

This program has been set to run in 8 threads. If this is going to overwhelm your machine, you can adjust the number of
threads by going into the `wsjRe.py` file, finding the `fetchSymbols()` function, and changing the number that appears in
this line: `with Pool(processes=8) as p:`

If you have any questions or concerns, send me an email. 
