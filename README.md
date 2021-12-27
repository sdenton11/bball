# bball
A repository of some basketball projects.

Note, this summary will try to describe set up in such a simple way that anyone should be able to use it. We will start with overall setup, followed by explanations of specific projects.

## Setup
1. The first step was getting to this page, already done.
2. The next step will be teaching you how to look like a coder and use terminal. Terminal is an application you'll use to run commands. It looks super intimidating but it's not.
3. Search for "Terminal" on your mac.
4. Type `cd ~/Desktop` and hit Enter. `cd` allows you to go places.
	1. Type `ls` and hit Enter to get your bearings. This is your current PLACE in your laptop. I suggest just putting these files in this folder — your Desktop. You can put them somewhere else, but you'll just need to navigate there. For example, if want to put them in my Documents I type `cd ~/Documents` and hit Enter.
5. Download this directory by running `git clone https://github.com/sdenton11/bball.git`
	1. You should now have all these files in a directory called `bball`
6. Type `cd bball` and hit Enter
7. Type `pip3 install -r requirements.txt` and hit Enter
8. This is all the set up required!

## Splits

This is just a basic project to allow you to look at splits for a player that are 2 standard deviations from the other splits in the group. As of right now, we only support files that are EXACTLY formatted like the files in this packages in `Splits/Data/stephen curry.csv`. This means it must have:
1. Formatted title of "player_name.csv"
2. Two rows before the names of the columns of data 
3. FOUR rows of column names to break apart the four types of splits. 

Right now we support four groups of splits:
1. game_result — split based on the outcome of the game
2. time — split based on when the game was played (Month, day of week, etc.)
3. opponent — split based on who the player was playing
4. location — split based on where the player played

Okay jesus Sam, how do I use the damn thing!!!!

Step 1: Put the file of interest in the `bball/Split/Data` folder

Step 2: Open terminal, navigate to split (if you followed my directions this would be `cd ~/Desktop/bball/Split`

Step 3: Run the script by typing `python3 process_data.py Data/ --s SPLIT_CATEGORY --p PLAYER_NAMES `

For example, try `python3 process_data.py Data/  --s opponent --p steph`

If you leave anything blank, it will run it for all of that category. For example, let's get all player's game result splits: `python3 process_data.py Data/ --s game_result`

That should be it for now!
