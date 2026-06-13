# companion_manager.py - 伴生种植管理

# 配置常量
FARM_SIZE = 16
# 简化版本
COMPANION_ZONE = [(2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8),
				  (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (11, 9), (12, 9), (13, 9),
				  (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10), (12, 10), (13, 10),
				  (2, 11), (3, 11), (4, 11), (5, 11), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11), (11, 11), (12, 11), (13, 11),
				  (2, 12), (3, 12), (4, 12), (5, 12), (6, 12), (7, 12), (8, 12), (9, 12), (10, 12), (11, 12), (12, 12), (13, 12),
				  (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13), (11, 13), (12, 13), (13, 13),
				  (2, 14), (3, 14), (4, 14), (5, 14), (6, 14), (7, 14), (8, 14), (9, 14), (10, 14), (11, 14), (12, 14), (13, 14),
				  (2, 15), (3, 15), (4, 15), (5, 15), (6, 15), (7, 15), (8, 15), (9, 15), (10, 15), (11, 15), (12, 15), (13, 15)]

companion_needs = {}

def move_to(x, y):
	for (x, y) in COMPANION_ZONE:
		move_to(x, y)

def get_valid_position(x, y):
	#"""处理边界循环"""
	while x < 0:
		x += FARM_SIZE
	while x >= FARM_SIZE:
		x -= FARM_SIZE
	while y < 0:
		y += FARM_SIZE
	while y >= FARM_SIZE:
		y -= FARM_SIZE
	return (x, y)

def collect_companion_info():
	#"""收集所有植物的伴生需求"""
	companion_needs.clear()
	
	for (x, y) in COMPANION_ZONE:
		move_to(x, y)
		result = get_companion()
		
		if result != None:
			plant_type, target_pos = result
			target_pos = get_valid_position(target_pos[0], target_pos[1])
			if target_pos not in companion_needs:
				companion_needs[target_pos] = []
			companion_needs[target_pos].append({
				'source_pos': (x, y),
				'plant_type': plant_type
			})

def is_needed_as_companion(pos):
	#"""检查指定位置是否被其他植物需要作为伴生"""
	for source_pos in companion_needs:
		for need in companion_needs[source_pos]:
			if need.get('source_pos') == pos:
				return need['plant_type']
	return None

def plant_for_companion(pos):
	#"""在指定位置种植所需的伴生植物"""
	needed_type = is_needed_as_companion(pos)
	if needed_type == None:
		return False
	
	x, y = pos
	move_to(x, y)
	
	current_entity = get_entity_type()
	if current_entity != None and current_entity != Entities.Dead_Pumpkin:
		return False
	
	if needed_type == Entities.Carrot:
		if get_ground_type() != Grounds.Soil:
			till()
		if num_items(Items.Carrot) > 0:
			plant(Entities.Carrot)
			return True
	elif needed_type == Entities.Grass:
		if num_items(Items.Hay) > 0:
			plant(Entities.Grass)
			return True
	elif needed_type == Entities.Tree:
		if num_items(Items.Wood) > 0:
			plant(Entities.Tree)
			return True
	elif needed_type == Entities.Bush:
		if num_items(Items.Wood) > 0:
			plant(Entities.Bush)
			return True
	return False

def optimize_companion_planting():
	#"""优化伴生种植布局"""
	collect_companion_info()
	
	if not companion_needs:
		return
	
	# 按照被需求次数排序 - 使用冒泡排序
	positions = list(companion_needs.keys())
	n = len(positions)
	
	for i in range(n):
		for j in range(0, n - i - 1):
			# 比较两个位置的需求次数
			count_j = len(companion_needs[positions[j]])
			count_j1 = len(companion_needs[positions[j + 1]])
			# 降序排列，需求多的在前
			if count_j < count_j1:
				positions[j], positions[j + 1] = positions[j + 1], positions[j]
	
	sorted_positions = positions
	
	# 优先满足被需求最多的位置
	for pos in sorted_positions:
		move_to(pos[0], pos[1])
		
		if get_entity_type() in (None, Entities.Dead_Pumpkin):
			# 统计最需要的植物类型
			type_counts = {}
			for need in companion_needs[pos]:
				t = need['plant_type']
				type_counts[t] = type_counts.get(t, 0) + 1
			
			if type_counts:
				# 选择被需求最多的植物类型
				best_type = max(type_counts, key=type_counts.get)
				
				if best_type == Entities.Carrot:
					if get_ground_type() != Grounds.Soil:
						till()
					if num_items(Items.Carrot) > 0:
						plant(Entities.Carrot)
				elif best_type == Entities.Grass:
					if num_items(Items.Hay) > 0:
						plant(Entities.Grass)
				elif best_type == Entities.Tree:
					if num_items(Items.Wood) > 0:
						plant(Entities.Tree)
				elif best_type == Entities.Bush:
					if num_items(Items.Wood) > 0:
						plant(Entities.Bush)