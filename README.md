# Paper Soccer RL Environment

This code is python code of Environment for Reinforcement Learning for game:  

**Paper Soccer**
https://en.wikipedia.org/wiki/Paper_soccer

![sample image](assets/sample.png)  

## Dependencies
Image preview is implemented and it depends on:
- opencv
- numpy
(basic code only so any version should work fine)

## Interface
Board class (inside [papersoccer_env.py](papersoccer_env.py) file) has couple interesting functions/variables including:
- **possible_moves()** - gets dictionary o fpossibel moves
- **move(...)** - executes one of the move from possible moves returning outcome information
- **draw()** - prepares RGB uint8 image with current state visualization
- **data** variable containing board fields data

## Notebook/Quick Start
For quick start you can check [this notebook](env.ipynb).
(some more dependencies here)

## License
Code author: 
- [Błażej Matuszewski](https://github.com/bwosh)

The project is licensed upon:  
[Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)  
[![BY-NC-SA-4.0](./assets/by-nc-sa.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
