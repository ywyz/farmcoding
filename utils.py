# utils.py - 工具函数
from planting_logic import *
from sunflower_manager import *
from companion_manager import *



def move_to(x, y):
	# """移动到指定坐标"""
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)

def water_if_needed(threshold=0.6):
	# """当水分低于阈值时浇水"""
	if get_water() < threshold:
		if num_items(Items.Water) > 0:
			use_item(Items.Water)

def should_plant_tree_here():
	# """判断是否应该种植树木"""
	y = get_pos_y()
	if y % 2 == 0:
		return True
	return False

def water_all_zones():
	# """按优先级给所有区域浇水"""
	# 优先级1：南瓜区
	for (x, y) in PUMPKIN_ZONE:
		move_to(x, y)
		water_if_needed(0.6)
	
	# 优先级2：向日葵区
	for (x, y) in SUNFLOWER_ZONE:
		move_to(x, y)
		water_if_needed(0.6)
	
	# 优先级3：仙人掌区
	for (x, y) in CACTUS_ZONE:
		move_to(x, y)
		water_if_needed(0.3)
	
	# 优先级4：伴生区
	for (x, y) in COMPANION_ZONE:
		move_to(x, y)
		water_if_needed(0.3)

def harvest_snake_pattern():
	# """蛇形遍历收获所有地块"""
	for x in range(FARM_SIZE):
		if x % 2 == 0:
			y_range = range(FARM_SIZE)
		else:
			y_range = range(FARM_SIZE - 1, -1, -1)
		
		for y in y_range:
			move_to(x, y)
			process_tile()

def process_tile():
	#"""处理单个地块"""
	x, y = get_pos_x(), get_pos_y()
	
	# 特殊处理：宝藏直接收获
	if get_entity_type() == Entities.Treasure:
		harvest()
		return
	
	# 收获成熟植物
	if can_harvest():
		harvest()
	
	# 种植逻辑
	plant_based_on_zone()

def plant_based_on_zone():
	# """根据区域种植合适的植物"""
	x, y = get_pos_x(), get_pos_y()
	
	if (x, y) in PUMPKIN_ZONE:
		plant_pumpkin_if_needed()
	elif (x, y) in SUNFLOWER_ZONE:
		plant_sunflower_if_needed()
	elif (x, y) in CACTUS_ZONE:
		plant_cactus_if_needed()
	elif (x, y) in TREE_ZONE:
		plant_tree_if_needed()
	elif (x, y) in MAZE_ZONE:
		plant_bush_for_maze()
	else:
		plant_companion_if_needed()

def plant_pumpkin_if_needed():
	# """种植南瓜"""
	if get_entity_type() in (None, Entities.Dead_Pumpkin):
		if get_ground_type() != Grounds.Soil:
			till()
		if num_unlocked(Unlocks.Pumpkins) > 0 and num_items(Items.Carrot) > 0:
			plant(Entities.Pumpkin)

def plant_sunflower_if_needed():
	# """种植向日葵"""
	if get_entity_type() in (None, Entities.Dead_Pumpkin):
		if get_ground_type() != Grounds.Soil:
			till()
		if num_unlocked(Unlocks.Sunflowers) > 0:
			plant(Entities.Sunflower)

def plant_tree_if_needed():
	# """种植树木"""
	if get_entity_type() in (None, Entities.Dead_Pumpkin):
		if num_items(Items.Wood) > 0:
			plant(Entities.Tree)

def plant_bush_for_maze():
	# """种植灌木用于迷宫"""
	if get_entity_type() == Entities.Bush:
		return
	if get_entity_type() in (None, Entities.Dead_Pumpkin):
		if num_items(Items.Wood) > 0:
			plant(Entities.Bush)

def plant_cactus_if_needed():
	# """种植仙人掌"""
	if get_entity_type() in (None, Entities.Dead_Pumpkin):
		if get_ground_type() != Grounds.Soil:
			till()
		if num_unlocked(Unlocks.Cactus) > 0 and num_items(Items.Carrot) > 0:
			plant(Entities.Cactus)

def plant_companion_if_needed():
	# """种植伴生植物"""
	current = get_entity_type()
	if current in (None, Entities.Dead_Pumpkin):
		needed = is_needed_as_companion((get_pos_x(), get_pos_y()))
		if needed:
			plant_for_companion((get_pos_x(), get_pos_y()))
		else:
			# 默认交替种植
			if get_pos_y() % 3 == 0:
				plant_carrot()
			elif get_pos_y() % 3 == 1:
				plant_grass()
			else:
				plant_bush()

def plant_carrot():
	# """种植胡萝卜"""
	if get_ground_type() != Grounds.Soil:
		till()
	if num_items(Items.Carrot) > 0:
		plant(Entities.Carrot)

def plant_grass():
	# """种植草"""
	if num_items(Items.Hay) > 0:
		plant(Entities.Grass)

def plant_bush():
	# """种植灌木"""
	if num_items(Items.Wood) > 0:
		plant(Entities.Bush)