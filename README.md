This is a simulation of the envelope game described in [this paper](https://dl.dropboxusercontent.com/u/22769456/CWOL.pdf). It uses finite state automata to model strategies, and is implemented in Python.

## Structure
File | Description
-----|------------|
fsm.py|Defines classes for `Player1`s, `Player2`s, and `State`s
simulation.py|Actual mechanics of the game, including reproduction, mutation, and actual playing
trial.py|Defines various parameters and runs the function defined in `simulation.py`
utils.py|Various utility functions used in other files
draw_fsm.py|Uses the `PyGraphviz` library to draw strategy automata as graphs
visualize_strategies.py|High-level code that takes a population and draws them using functions defined in `draw_fsm.py`
tally_classifications.py|Takes data outputted by trial runs and aggregates data over time into a few files
analyze.py|Highest level visualization code. Takes data outputed by trial runs and aggregates data, visualizes strategies, and produces a packaged result.

## How to Use
* To run a trial, simply modify the parameters in trial.py, and run `python trial.py` from the command line
* To visualize the result, simply run `python analyze.py ./path/to/trial/directory/` from the command line
	* You can use the flag `--no-viz` after the path to the directory if you'd like to just look at strategy classifications over time, but don't want to see the visualized strategies themselves
* To look at the visualized result, `cd` into the trial directory (which should have files like `cooperate_continue_stats_0.json` in it), then run `cd analysis && python -m SimpleHTTPServer 8000`. Then, go to [http://localhost:8000/](http://localhost:8000/) in your browser.

## Example Trial Run Visualization
* For an example of the visualization generated by `analyze.py`, `cd` into the directory of this repository, then run `cd ./demo_results/analysis && python -m SimpleHTTPServer 8000`, and go to [http://localhost:8000/](http://localhost:8000/) in your browser.

<img src="http://araftery.s3.amazonaws.com/cwol_fsm/scrn1.jpg" style="width:100%;"/>
This is a stacked [area chart](http://en.wikipedia.org/wiki/Area_chart) of strategies over time. The "4% cooperate" statistic means that, 4% of all Player 1 moves, over all 10,000 generations, were "cooperate." Overlaid onto the graph is a line chart:

<img src="http://araftery.s3.amazonaws.com/cwol_fsm/scrn2.png" style="width:100%;"/>
This line chart shows the percentage of moves in each generation that were "cooperate." By choosing "% Cooperate at All," the line will switch to show the percentage of *games* in each generation in which "cooperate" was played *at least once*.

By hovering the cursor over the graph, the user can select a generation. Clicking will bring the user to a page showing the total population at that generation, with visualizations of the strategies in the population.
>Note: the included demo analysis does not include visualizations of strategies in order to keep the repo to a reasonable file size. These visualizations can get up to several GB in size. In order to generate these visualizations for the demo data, `cd` to the repo directory and execute: `python analyze.py ./demo/`.*

Visualizations for Player 1 strategies look like:

<img src="http://araftery.s3.amazonaws.com/cwol_fsm/dwol.png" />

Visualizations for Player 2 strategies look like:

<img src="http://araftery.s3.amazonaws.com/cwol_fsm/player2_strategy.png" style="width:100%;" />

## Requirements
* Required Python modules are listed in `requirements.txt`. These can be installed by `cd`ing to the repo directory and executing `[sudo] pip install -r requirements.txt`.
* In addition, for the PygraphViz library, [graphviz](http://www.graphviz.org/) is required
	* This is only required for generating visualizations of automata

## Contact
* If you have any questions, feel free to contact me at andrewra<span style="display:none;">nospam</span>ftery@gmail.com