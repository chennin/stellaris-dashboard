# Stellaris Dashboard

Stellaris currently does not have a timeline feature that shows some statistics and historical info, so I decided to build this project. 

Here is a one minute animation of the interactive dashboard, as available in-game:

https://gfycat.com/RealAnguishedAustralianfreshwatercrocodile

Alternatively, you can export static images:

https://imgur.com/a/4dhVd

The program runs in the background and reads the autosave files as they are generated by the game. It takes information out of them and compiles that into a database,
which is then used to visualize your progress in various ways.

So far, the dashboard includes information about your:

  - economy: detailed, categorized energy, mineral and food budgets (categories include production, sector income, trade, ship and pop maintenance, enclave trade deals...)
  - science: number of techs, research output, exploration (the number of surveyed objects)
  - demographics: number of pops, distribution of species
  - factions: size, support and happiness of each faction
  - military: fleet strength

For balance reasons, the dashboard completely ignores saves from Multiplayer and Ironman modes. 
To maintain immersion, only information which is reasonable for you to have is shown, so you can only see the military power of empires who are friendly, or who have given you active sensor links or defensive pacts. 
However, you can configure a cheat mode which shows everything.

# Installation and Use

The Stellaris dashboard requires Python 3.6, which you can download and install from https://www.python.org/.
It is mainly tested in Linux, but it should also work in Windows and theoretically Mac.

  1. Download and extract the repository.
  2. (Optional) create and activate a virtual environment using `virtualenv`. This avoids interfering with any other python programs you use or might use in the future.
  3. (Optional) Open a terminal or command line in the downloaded directory and run `pip install .` to install the program using pip. This should take care of all dependencies and allow you to run the program from anywhere. 
  4. Alternatively, use `pip install -r requirements.txt` to only install the dependencies, or install them manually. 
  5. To use the interactive dashboard in-game, copy the contents of the `mod/` folder into your Stellaris mod folder and enable the "Stellaris Dashboard Integration" mod in the game's launcher. Alternatively, you can use your regular browser to view the page.

Note: You may have to use `python -m pip install .` instead of `pip install .` if you use Windows. In this case, just replace `pip` with `python -m pip` wherever necessary.

# Instructions

If you just want the basics, run the `stellarisdashboard` command while you play the game and it should do everything for you. 

If you installed the program in step 3 above, run `stellarisdashboard` in your command line to launch the dashboard in default configuration or `stellarisdashboardcli` to execute specific commands, which are described below.

Otherwise, you can change your working directory to the `src/` folder and run `python -m stellarisdashboard` for the default program, or `python -m stellarisdashboard.cli` for the CLI if you did not install the program in step 3.

## Default Execution
The command `stellarisdashboard` reads the save files in the background and starts a local web server for the interactive dashboard. 

As the save files are processed in the background, the data is added to a database in your output folder. This database is named according to the game it represents.
Every file generated by the dashboard is saved in the output folder, which is by default `$USER/Documents/stellarisdashboard/`. Here, `$USER` is your user directory, which depends on your operating system.

You can access the visualizations while the dashboard is running, by either using a browser to go to `http://127.0.0.1:28053/`, or by using the included mod for the in-game browser. 

Note: The current method of reading the save files is a bit slow, so the graphs may lag behind the game quite a bit. For a 1000 star galaxy, reading a single save file can take about 30 seconds...

## Command Line Interface

The command line interface allows you to:

  - Only run the save monitoring without any interactivity. This only builds the database, which you can later visualize (`stellarisdashboardcli monitor_saves`)
  - Produce the static visualizations (`stellarisdashboardcli visualize`)
  - Reparse all existing files. Running `stellarisdashboard` or `stellarisdashboardcli monitor_saves` will ignore any existing save files,
  so sometimes it may be necessary to manually re-parse them. (`stellarisdashboardcli parse_saves`)

Any parameters provided to these commands override the values set in the `config.ini` file.

## Configuration

The following parameters can be specified in a config.ini file placed in the same folder as the stellarisdashboard/config.py file:

  - `save_file_path`: The path where the save files are.
  - `base_output_path`: The path where any files generated by the dashboard end up. This includes the database and any images you generate with `stellarisdashboardcli visualize`.
  - `threads`: The number of concurrent processes that are used for reading save files. (Recommended 2-3)
  - `colormap`: The colormap used when producing static images.
  - `port`:  The port where the webapp for the interactive dashboard is served. If you change this, you should adapt the URL in the 
  `mod/Timeline/interface/browser.gui` file accordingly.
  - `showeverything`: Set to `True` if you want to see the data of all empires.

# Hardware Requirements

The Hardware requirements depend on many factors:

  - how fast you play
  - the galaxy size
  - how frequently you generate autosaves (monthly, quarterly, yearly)
  - how often you pause the game. 

### CPU
If the dashboard cannot keep up, it will likely skip some saves as they are overwritten by the game and it will skip some data points.

If you have a quad-core CPU or better, I suggest allowing 2 or 3 threads. By default, the dashboard uses one or (n/2) - 1 threads, whichever is higher.

### Disk Space
As for disk space, the dashboard has a fairly small footprint. The database currently uses about 1 MB every ten years with monthly autosaves.
Each game's data is stored in a separate database in your output folder, so you can delete them individually if you wish. 

The game deletes the autosaves in a "rolling" manner, so only the most recent saves are kept. If you plan a long game 
and want to be able to re-generate the database later, you need to continually backup the save files. This can be done by
running a script that automatically copies them to another folder.

This uses a lot more disk space (in my experience about 1 GB every 50 years), but allows you to rebuild the full database at any point using 
`stellarisdashboardcli parse_saves --save-path path/to/your/save_backup`. 

# Bugs

Some known bugs:

  - the economic budget numbers might not exactly match with what is shown in-game. This is because the program almost definitely misses many modifiers. However, most numbers should be accurate enough to get a decent idea.
  - Sometimes the dashboard glitches and adds a line that crosses through most of the graphs. This probably happens because different parts of the program interact with the database at the same time. When this happens, simply kill the program and start it again.
  - The food budget does not match the in-game numbers exactly when sectors are involved. It probably won't deviate too far. This is hard to fix because food is only shown as an integer value in-game.

The program should be fairly stable, but if something weird happens, just restart the app! 


