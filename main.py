# main.py - 优化后的农场管理主程序
from utils import *
from sunflower_manager import *
from planting_logic import *
from companion_manager import *

def main():
	while True:
		# 第一阶段：水分管理
		water_all_zones()
		
		# 第二阶段：南瓜区管理（最高优先级）
		manage_pumpkin_patch()
		
		# 第三阶段：向日葵区管理（能量优先）
		optimize_sunflower_harvest()
		
		# 第四阶段：蛇形遍历处理所有地块
		harvest_snake_pattern()
		
		# 第五阶段：伴生优化（混合种植）
		if num_unlocked(Unlocks.Polyculture) > 0:
			optimize_companion_planting()