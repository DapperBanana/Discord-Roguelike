game_map_width = 3
game_map_height = 3
game_map_depth = 3
game_map_info = 3
game_map_side_length = 3
game_map_list = [[[[0 for i in range(game_map_info)] for z in range(game_map_side_length)] for y in range(game_map_side_length)] for x in range(game_map_side_length)]
print(game_map_list)
for z in range(len(game_map_list)):
    for y in range(len(game_map_list[0])):
        for x in range(len(game_map_list[0][0])):
            game_map_list[z][y][x] = [x+1, y+1, z+1]
print(game_map_list)


cube3d = [[
            [[0,0,0], [1,0,0], [2,0,0]],
            [[0,1,0], [1,1,0], [2,1,0]],
            [[0,2,0], [1,2,0], [2,2,0]],
        
        ],[
            
            [[0,0,1], [1,0,1], [2,0,1]],
            [[0,1,1], [1,1,1], [2,1,1]],
            [[0,2,1], [1,2,1], [2,2,1]],
            
        ],[                 
            
            [[0,0,2], [1,0,2], [2,0,2]],
            [[0,1,2], [1,1,2], [2,1,2]],
            [[0,2,2], [1,2,2], [2,2,2]],
         ]]