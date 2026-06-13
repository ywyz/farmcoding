# sunflower_manager.py - 向日葵管理

# 配置常量
MIN_SUNFLOWERS_FOR_BONUS = 10
MIN_PETALS_THRESHOLD = 7
SUNFLOWER_ZONE = [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7),
				  (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7),
				  (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7),
				  (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (11, 5), (11, 6), (11, 7),
				  (12, 0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7),
				  (13, 0), (13, 1), (13, 2), (13, 3), (13, 4), (13, 5), (13, 6), (13, 7)]

sunflower_petals = {}

def move_to(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)

def update_sunflower_petals():
	pos = (get_pos_x(), get_pos_y())
	if get_entity_type() == Entities.Sunflower:
		petals = measure()
		if petals != None:
			sunflower_petals[pos] = petals

def get_max_petals():
	if len(sunflower_petals) == 0:
		return 0
	max_p = 0
	for pos in sunflower_petals:
		if sunflower_petals[pos] > max_p:
			max_p = sunflower_petals[pos]
	return max_p

def should_harvest_sunflower():
	pos = (get_pos_x(), get_pos_y())
	if pos not in sunflower_petals:
		return False
	current_petals = sunflower_petals[pos]
	max_petals = get_max_petals()
	
	if current_petals < MIN_PETALS_THRESHOLD:
		return True
	
	return current_petals == max_petals and max_petals >= 7

def harvest_sunflower():
	update_sunflower_petals()
	if should_harvest_sunflower():
		harvest()
		pos = (get_pos_x(), get_pos_y())
		if pos in sunflower_petals:
			sunflower_petals.pop(pos)
		return True
	return False

def count_mature_sunflowers():
	# """统计成熟向日葵数量"""
	count = 0
	for (x, y) in SUNFLOWER_ZONE:
		move_to(x, y)
		if get_entity_type() == Entities.Sunflower and can_harvest():
			count += 1
	return count

def optimize_sunflower_harvest():
	# 优化向日葵收获策略"""
	update_sunflower_petals()
	
	mature_count = count_mature_sunflowers()
	
	# 只有当向日葵数量足够时才寻求8倍加成
	if mature_count >= MIN_SUNFLOWERS_FOR_BONUS:
		max_petals = get_max_petals()
		
		# 优先收获花瓣最多的向日葵
		for pos, petals in sunflower_petals.items():
			if petals == max_petals and petals >= MIN_PETALS_THRESHOLD:
				move_to(pos[0], pos[1])
				if can_harvest():
					harvest()
					if pos in sunflower_petals:
						sunflower_petals.pop(pos, None)
				break
	
	# 收获剩余成熟向日葵
	for (x, y) in SUNFLOWER_ZONE:
		move_to(x, y)
		if get_entity_type() == Entities.Sunflower and can_harvest():
			harvest()
			if (x, y) in sunflower_petals:
				sunflower_petals.pop((x, y), None)