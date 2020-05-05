Flappy Bird ML w/ Evolution
---------------------------
In this project, there are 3 files, we will cover them all here.

flappybird.py:
-------------
This is the main game and the base of it all.
You press the `SPACE BAR` to play, and make points.

flappybird_copycat.py:
------------------
This is a more advanced game.
You can play as if it's a regular game, 
but the game records your movements at all time.
When you feel like it, press the `S` button, and the AI that was watching you (and was learning from you), 
will start 'play' for you. You will notice it has simillar movements to you, after all,
you are the only player it knows.

flappybird_evolution.py:
----------
This one is based only on trying to teach the program how to play the game by itself.
In oppose to the other files, or "games", this one is not playable by you, only by the program.
It uses an evolution algorithm to make new improved birds at any generation, 
until the fittest bird is born.
Again, you can only watch as the program is advancing itself.
