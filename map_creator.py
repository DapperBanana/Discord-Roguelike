import os
import os.path
import os
import glob
import time
import random
import numpy

walls = "#"
floor = " "
void = "-"
player = "&"

#set up width and height
room_width, room_height= (40,40)

#First set the entire grid to void characters
grid_array = [[void for i in range(room_height)] for j in range(room_width)]

#Create the controller in the middle of the room
controller_x = int(room_width / 2)
controller_y = int(room_height / 2)
player_x = controller_x
player_y = controller_y
#random direction with:
#0 = north
#1 = east
#2 = south
#3 = west
direction = random.randint(0,3) 
#create steps for how large you want the room to be (try to not have it be larger than the total square footage of the space)
steps = room_width * room_height
direction_change_odds = 1

for x in range(steps):
    grid_array[controller_y][controller_x] = floor
    x_direction = 0
    y_direction = 0
    #randomize the direction
    if(random.randint(0,direction_change_odds) == direction_change_odds):
        direction = random.randint(0,3)
    
    #move the controller
    if direction == 0:
        y_direction = -1
    elif direction ==1:
        x_direction = 1
    elif direction == 2:
        y_direction = 1
    elif direction == 3:
        x_direction = -1
    
    controller_x += x_direction
    controller_y += y_direction
    
    #Ensure that we didn't go outside the grid
    if(controller_x < 2 or controller_x >= room_width - 2):
        controller_x += -x_direction * 2
    if(controller_y < 2 or controller_y >= room_height - 2):
        controller_y += -y_direction * 2

for y in range(1,room_height-1):
    for x in range(1,room_height-1):
        if grid_array[y][x] != floor:
            top = grid_array[y-1][x]
            left = grid_array[y][x-1]
            right = grid_array[y][x+1]
            bottom = grid_array[y+1][x]
            if top == floor or left == floor or right == floor or bottom == floor:
                grid_array[y][x] = walls

grid_array[player_y][player_x] = player
#Now lets open a txt doc and write this shit
numpy.savetxt("test.txt", grid_array, fmt='%s')






#__________.__                                    .__               
#\______   \  | _____  ___.__. ___________  ___  _|__| ______  _  __
# |     ___/  | \__  \<   |  |/ __ \_  __ \ \  \/ /  |/ __ \ \/ \/ /
# |    |   |  |__/ __ \\___  \  ___/|  | \/  \   /|  \  ___/\     / 
# |____|   |____(____  / ____|\___  >__|      \_/ |__|\___  >\/\_/  
#                    \/\/         \/                      \/   

#Next lets grab what the player can see (this is multiplied by 2, this is + AND - player x and same with y)
player_view_x,player_view_y = (5, 5)
#And lastly create the viewable map
viewable_grid = [[0 for x in range(player_view_y*2+1)] for y in range(player_view_x*2+1)]

#Grab the north right coordinates and the south left coordinates to box the user in
north_left_x = (player_x - player_view_x)
north_left_y = (player_y - player_view_y)
south_right_x = (player_x + player_view_x)
south_right_y = (player_y + player_view_y)

#Create the grid constraints
if north_left_x < 0:
    #too far to the left
    viewable_grid_x_start = 0
elif south_right_x >= room_width:
    #too far to the right
    viewable_grid_x_start = north_left_x - (south_right_x - (room_width - 1))
else:
    #within bounds
    viewable_grid_x_start = north_left_x

if north_left_y < 0:
    #too far up
    viewable_grid_y_start = 0
elif south_right_y >= room_height:
    #too far down
    viewable_grid_y_start = north_left_y - (south_right_y - (room_height - 1))
else:
    #within bounds
    viewable_grid_y_start = north_left_y

for y in range(player_view_x*2+1):
    for x in range(player_view_x*2+1):
        viewable_grid[y][x] = grid_array[y + viewable_grid_y_start][x + viewable_grid_x_start]

numpy.savetxt("test_view.txt", viewable_grid, fmt='%s')

