Endless Racing
Top-down endless road game in Pygame. The road curves on its own. You stay on it by sliding left and right in the lane.
Run
pip install pygame
python main.py
Run it from this folder so from src.player import Player works.
Controls
W / Up — Accelerate
S / Down — Brake, then reverse
A / Left — Slide left in the lane
D / Right — Slide right in the lane
The car stays lined up with the road. Steering only shifts you across the lane and leans the car a little. Leaving the asphalt slows you down.
Files
main.py — window, road generation, camera, drawing
src/player.py — arcade car (speed, lane offset, lean)
