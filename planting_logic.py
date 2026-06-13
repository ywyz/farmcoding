# planting_logic.py - 种植逻辑

# 配置常量
MAX_DEAD_PUMPKINS_BEFORE_FERTILIZER = 3
PUMPKIN_ZONE = [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
				(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
				(4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
				(5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
				(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
				(7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]

def move_to(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)

def manage_pumpkin_patch():
	# 统计枯萎南瓜数量
	dead_count = 0
	
	# 检查并补种枯萎南瓜
	for (x, y) in PUMPKIN_ZONE:
		move_to(x, y)
		if get_entity_type() == Entities.Dead_Pumpkin:
			dead_count += 1
			# 立即补种
			till()
			if num_unlocked(Unlocks.Pumpkins) > 0 and num_items(Items.Carrot) > 0:
				plant(Entities.Pumpkin)
	
	# 枯萎过多时使用肥料加速
	if dead_count > MAX_DEAD_PUMPKINS_BEFORE_FERTILIZER:
		if num_items(Items.Fertilizer) > 0:
			for (x, y) in PUMPKIN_ZONE:
				move_to(x, y)
				if get_entity_type() == Entities.Pumpkin:
					use_item(Items.Fertilizer)
					# 使用奇异物质治愈感染
					if num_items(Items.Weird_Substance) > 0:
						use_item(Items.Weird_Substance)