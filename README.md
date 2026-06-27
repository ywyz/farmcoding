# TFWR 16x16 自动化农场项目介绍

本项目是 The Farmer Was Replaced 的 16x16 自动化农场脚本。目标是在维持全作物覆盖的同时尽量提高收益：核心区产南瓜、仙人掌、迷宫金币，向日葵采用固定区 + 补给区混种来补足电力，补给区持续产胡萝卜、树、灌木和草，主循环会按条件穿插恐龙模式获取骨头。

## 快速开始

### 常规农场入口

运行 `auto_farm.py`：

```python
from farm_main import main

main()
```

这会进入普通 16x16 混合农场主循环。

### 恐龙模式入口

运行 `dino_mode.py`：

```python
main()
```

恐龙模式会循环执行：

1. 如果有仙人掌库存，切换恐龙帽并按蛇形路径走完整个农场。
2. 切回草帽。
3. 执行普通农场维护周期，让常规资源继续增长。

当前普通维护周期数量由 `dino_mode.py` 中的 `DINO_NORMAL_CYCLES = 3` 控制。

## 项目结构

| 文件                 | 职责                                                               |
| -------------------- | ------------------------------------------------------------------ |
| `auto_farm.py`     | 常规农场启动入口，只负责导入并运行`farm_main.main()`。           |
| `farm_main.py`     | 主循环调度层，负责建布局、循环维护、库存日志、区域级并行任务。     |
| `farm_layout.py`   | 16x16 布局配置和坐标归属判断，决定每个格子应该种什么。             |
| `farm_zones.py`    | 各种植区域的具体维护逻辑：南瓜、向日葵、仙人掌、迷宫、补给区。     |
| `farm_utils.py`    | 通用工具层：移动、种植、浇水、施肥、解锁、无人机、日志、扫描路径。 |
| `dino_mode.py`     | 恐龙模式入口和循环逻辑。                                           |
| `project_notes.md` | 详细开发记录、历史决策和路线图。                                   |
| `__builtins__.py`  | 游戏内置 API 类型提示，只读参考，不要修改。                        |
| `save.json`        | 游戏存档，不要手动修改。                                           |

## 当前 16x16 布局

布局入口在 `farm_layout.py`。

| 区域       | 坐标/大小              | 目标                               |
| ---------- | ---------------------- | ---------------------------------- |
| 南瓜区     | `(0,0)` 起，`8x8`  | 维护巨型南瓜产出。                 |
| 向日葵区   | `(8,0)` 起，`8x4`  | 成熟即收，稳定产电。               |
| 仙人掌区   | `(12,4)` 起，`4x4` | 成熟后排序并触发连锁收获。         |
| 迷宫灌木点 | `(8,8)`              | 种灌木，生成迷宫并收金币。         |
| 补给区     | 其余格子               | 混种向日葵、胡萝卜、树、灌木和草。 |

补给区不是单一作物区。`zone_at(x, y)` 会在非核心区按确定性规则混种：

- 约四分之一补给格种向日葵，避免电力被无人机移动消耗光。
- 少量草地固定保留，稳定获取干草。
- 树使用棋盘格位置，避免正交相邻导致生长变慢。
- 其余格子在胡萝卜和灌木之间分配。

`target_entity_at(x, y)` 是最终作物决策入口。新增或调整作物布局时，优先修改这里和相关 `is_*_zone()` 函数。

## 运行流程

### 常规主循环

`farm_main.main()`：

1. `build_mixed_layout()` 清场并重建基础布局。
2. 进入无限循环。
3. 打印运行状态和库存。
4. 如果 `PARALLEL_ENABLED = True`，执行 `maintain_mixed_layout_parallel()`。
5. 否则执行 `maintain_mixed_layout()`。
6. 每隔 `DINO_LOOP_INTERVAL` 轮且仙人掌库存足够时，自动运行一次恐龙模式并重建农场。

### 建布局

`build_mixed_layout()` 会按顺序维护：

1. 南瓜区
2. 向日葵区
3. 仙人掌区
4. 迷宫灌木点
5. 补给区

注意：这个函数会先 `clear_and_home()`，因此只应该在初始化、迷宫收获后重建、恐龙模式回到普通农场时使用。

### 普通串行维护

`maintain_mixed_layout()` 按阶段维护所有区域，并在每个阶段后打印 `phase_ticks`。迷宫不是每轮都跑，而是由 `MAZE_COOLDOWN_LOOPS` 控制频率。

### 区域级并行维护

`maintain_mixed_layout_parallel()` 使用区域级 + 补给分片模型：

- 向日葵 1 个任务，扫描固定区和补给混种位
- 补给区按行切成多个任务
- 南瓜区 1 个任务
- 仙人掌区 1 个任务

补给任务会跳过向日葵格，避免和向日葵任务写同一个格子。这样能减少“上方补给区最后完成导致整轮等待”的问题。

## 主要配置

配置集中在 `farm_utils.py` 和 `farm_layout.py`。

| 配置                                                 | 当前含义                                                      |
| ---------------------------------------------------- | ------------------------------------------------------------- |
| `DEBUG = True`                                     | 开启调试日志。                                                |
| `PARALLEL_ENABLED = True`                          | 使用区域级并行维护。                                          |
| `PARALLEL_ROLLOUT_LEVEL = PARALLEL_ROLLOUT_SERIAL` | 旧的区域内分片 rollout 默认关闭，避免干扰区域专属无人机模型。 |
| `WATER_LOW = 0.50`                                 | 普通补水阈值。                                                |
| `WATER_HIGH = 0.75`                                | 高价值区补水阈值。                                            |
| `FERTILIZER_MIN = 20`                              | 肥料库存高于该值才自动施肥。                                  |
| `MAZE_COOLDOWN_LOOPS = 3`                          | 每 3 轮尝试一次迷宫。                                         |
| `SUNFLOWER_MAX_HARVESTS_PER_LOOP = 4`              | 每轮最多收获的最高花瓣向日葵数量。                            |
| `SUPPLY_MIN_WORKERS = 2`                           | 补给区最少分片任务数。                                        |
| `DINO_ENABLED = True`                              | 主循环允许自动穿插恐龙模式。                                  |
| `DINO_LOOP_INTERVAL = 8`                           | 每 8 轮普通维护尝试一次恐龙模式。                             |
| `DINO_MIN_CACTUS = 16`                             | 仙人掌库存低于该值时跳过恐龙模式。                            |
| `DINO_NORMAL_CYCLES = 3`                           | 恐龙模式后穿插的普通农场维护轮数。                            |

## 函数地图

### `auto_farm.py`

| 函数/入口  | 作用                                     |
| ---------- | ---------------------------------------- |
| `main()` | 来自`farm_main.py`，启动常规混合农场。 |

### `farm_main.py`

| 函数                                 | 作用                                                                       |
| ------------------------------------ | -------------------------------------------------------------------------- |
| `print_inventory()`                | 打印核心库存：干草、木头、胡萝卜、南瓜、仙人掌、电力、水、肥料、奇异物质。 |
| `print_runtime_status()`           | 打印并行状态、无人机数量、当前位置、世界大小。                             |
| `build_mixed_layout()`             | 清场并按当前布局重建所有区域。                                             |
| `maintain_mixed_layout()`          | 串行维护完整农场。                                                         |
| `maintain_mixed_layout_parallel()` | 区域级并行维护完整农场。                                                   |
| `main()`                           | 常规农场主入口。                                                           |

### `farm_layout.py`

| 函数/常量                   | 作用                         |
| --------------------------- | ---------------------------- |
| `PUMPKIN_*`               | 南瓜区起点和尺寸。           |
| `SUNFLOWER_*`             | 向日葵区起点和尺寸。         |
| `CACTUS_*`                | 仙人掌区起点和尺寸。         |
| `MAZE_X`, `MAZE_Y`      | 迷宫灌木点。                 |
| `world_size()`            | 返回当前世界大小。           |
| `wrap(value)`             | 把坐标包回地图范围。         |
| `in_rect(...)`            | 判断坐标是否在矩形区域内。   |
| `is_pumpkin_zone(x, y)`   | 判断是否为南瓜区。           |
| `is_sunflower_zone(x, y)` | 判断是否为向日葵区。         |
| `is_cactus_zone(x, y)`    | 判断是否为仙人掌区。         |
| `is_maze_bush_tile(x, y)` | 判断是否为迷宫灌木点。       |
| `is_supply_zone(x, y)`    | 判断是否为补给区。           |
| `zone_at(x, y)`           | 返回坐标所属区域名称。       |
| `target_entity_at(x, y)`  | 返回坐标应该种植的实体。     |
| `tree_allowed_at(x, y)`   | 判断树区中该格是否允许种树。 |

### `farm_utils.py`

| 函数                                                         | 作用                                   |
| ------------------------------------------------------------ | -------------------------------------- |
| `log(...)`, `log_timing(...)`                            | 调试和性能日志。                       |
| `parallel_rollout_at_least(...)`、`*_parallel_enabled()` | 旧分片并行开关判断。当前主要保留兼容。 |
| `parallel_rollout_name()`                                  | 返回 rollout 名称。                    |
| `wrap(...)`, `mod(...)`                                  | 坐标和取模工具。                       |
| `wait_two_seconds()`                                       | 用`do_a_flip()` 等待。               |
| `go_x(...)`, `go_y(...)`, `go_to(...)`                 | 移动到指定坐标。                       |
| `ensure_soil()`                                            | 确保当前地块是土壤。                   |
| `ensure_grassland()`                                       | 确保当前地块是草地。                   |
| `water_if_needed(level)`                                   | 水位不足时浇水。                       |
| `fertilize_if_needed()`                                    | 肥料足够时施肥。                       |
| `safe_harvest()`                                           | 仅在可收获时收获。                     |
| `clear_and_home()`                                         | 清场并回到`(0,0)`。                  |
| `can_pay(cost)`                                            | 判断库存是否足够支付成本。             |
| `can_plant(entity)`                                        | 判断是否有足够资源种植实体。           |
| `plant_if_empty(entity)`                                   | 空地时种植。                           |
| `clear_wrong_entity(target_entity)`                        | 清除不符合目标的实体。                 |
| `force_plant(target_entity)`                               | 尽力种植目标实体。                     |
| `plant_grass_crop(...)`                                    | 在草地作物区种植。                     |
| `plant_soil_crop(...)`                                     | 在土壤作物区种植。                     |
| `replace_with(...)`                                        | 替换当前格为目标实体。                 |
| `plant_zone_tile(...)`                                     | 按实体类型选择合适地形并种植。         |
| `try_unlock_one(...)`, `try_unlocks()`                   | 自动尝试解锁。                         |
| `safe_spawn(...)`, `run_or_spawn(...)`                   | 安全创建无人机任务，失败时本地执行。   |
| `wait_all(handles)`                                        | 等待所有无人机任务完成。               |
| `cleanup_finished(handles)`                                | 清理已完成任务句柄。                   |
| `shard_rows(...)`                                          | 旧区域内分片工具。                     |
| `scan_rect(...)`                                           | 生成蛇形扫描坐标。                     |
| `coord_key(...)`, `count_coord_conflicts(...)`           | 检查计划坐标冲突。                     |
| `stage_barrier(name)`                                      | 阶段屏障日志。                         |

### `farm_zones.py`

| 函数                                           | 作用                                                   |
| ---------------------------------------------- | ------------------------------------------------------ |
| `opposite(...)`, `index_to_direction(...)` | 方向辅助。                                             |
| `key_for(...)`, `step_coord(...)`          | 迷宫路径坐标辅助。                                     |
| `direction_priority_toward(...)`             | 迷宫 DFS 的目标导向方向排序。                          |
| `maze_substance_needed()`                    | 计算生成迷宫所需奇异物质。                             |
| `maze_dfs_to_treasure(...)`                  | 目标导向 DFS 搜索宝藏。                                |
| `maintain_maze_bush_tile()`                  | 维护迷宫灌木、生成迷宫、收获宝藏。                     |
| `maintain_pumpkin_tile()`                    | 维护单个南瓜格。                                       |
| `maintain_pumpkin_row_range(...)`            | 旧南瓜分片维护。                                       |
| `maintain_pumpkin_zone_tiles_parallel()`     | 旧南瓜区域内分片并行维护。                             |
| `pumpkin_zone_has_dead()`                    | 检查并补种死南瓜。                                     |
| `pumpkin_zone_complete()`                    | 判断南瓜区是否完整。                                   |
| `find_and_harvest_pumpkin()`                 | 查找可收获南瓜。                                       |
| `try_harvest_pumpkin_at(...)`                | 尝试收获指定偏移点。                                   |
| `quick_harvest_pumpkin()`                    | 优先检查角落和中心点，快速收南瓜。                     |
| `maintain_pumpkin_zone()`                    | 完整维护南瓜区。                                       |
| `maintain_sunflower_zone()`                  | 维护固定区和混种向日葵，优先收最高花瓣以触发电力倍率。 |
| `maintain_sunflower_row_range(...)`          | 旧向日葵分片维护。                                     |
| `maintain_sunflower_zone_tiles_parallel()`   | 旧向日葵区域内分片并行维护。                           |
| `cactus_value_at(...)`                       | 读取仙人掌测量值。                                     |
| `cactus_zone_ready()`                        | 判断仙人掌区是否全部成熟。                             |
| `cactus_zone_sorted()`                       | 判断仙人掌是否已按行列排序。                           |
| `cactus_horizontal_pass()`                   | 仙人掌横向冒泡交换。                                   |
| `cactus_vertical_pass()`                     | 仙人掌纵向冒泡交换。                                   |
| `sort_cactus_zone()`                         | 循环排序仙人掌区。                                     |
| `maintain_cactus_zone()`                     | 完整维护仙人掌区。                                     |
| `maintain_supply_tile(...)`                  | 维护单个补给格。                                       |
| `maintain_supply_row_range(...)`             | 旧补给分片维护。                                       |
| `maintain_supply_zone_parallel()`            | 旧补给区域内分片并行维护。                             |
| `maintain_supply_zone()`                     | 完整维护补给区。                                       |

### `dino_mode.py`

| 函数                               | 作用                                                 |
| ---------------------------------- | ---------------------------------------------------- |
| `move_if_possible(direction)`    | 恐龙模式安全移动。                                   |
| `snake_fill_walk()`              | 蛇形走完整个世界。                                   |
| `run_dinosaur_mode()`            | 检查解锁和仙人掌库存，切恐龙帽、蛇形移动、切回草帽。 |
| `run_normal_mode_cycles(cycles)` | 恐龙后运行若干轮普通农场维护。                       |
| `run_dinosaur_loop()`            | 恐龙模式循环。                                       |
| `dino_main()`                    | 恐龙模式主逻辑。                                     |
| `main()`                         | 恐龙模式入口。                                       |

## 开发规则和注意事项

1. 这个运行环境不是完整 Python。不要使用 `import as`、三引号注释、复杂标准库能力。
2. 优先使用 `from module import name` 或 `from module import *`。
3. `till()` 是地形切换，不是单向翻土；调用前必须知道当前地形。
4. `can_harvest()` 不代表当前实体是目标作物。收获高价值作物前先检查 `get_entity_type()`。
5. `move()` 在普通模式下会地图环绕；恐龙模式下要优先使用 `can_move()` 避免撞到身体。
6. 新增区域时先改 `farm_layout.py`，再在 `farm_zones.py` 增加维护函数，最后接入 `farm_main.py`。
7. 区域级并行优先于区域内分片。新增无人机任务时要保证一个区域只有一个写者。
8. 修改恐龙模式时注意它会 `clear()`，所以要通过普通维护周期恢复农场资源。

## 常见开发任务

### 调整区域大小

改 `farm_layout.py` 中的区域常量，然后检查：

- `is_*_zone()` 是否仍然互不重叠。
- `MAZE_X`, `MAZE_Y` 是否没有落入其他核心区域。
- `target_entity_at()` 是否能覆盖所有补给区格子。

### 新增一种作物区域

1. 在 `farm_layout.py` 新增区域常量和 `ZONE_*` 名称。
2. 新增 `is_new_zone(x, y)`。
3. 在 `is_supply_zone()` 中排除新区域。
4. 在 `zone_at()` 中返回新区域。
5. 在 `target_entity_at()` 中返回目标实体。
6. 在 `farm_zones.py` 写 `maintain_new_zone()`。
7. 在 `farm_main.py` 串行和并行流程里接入。

### 调整资源均衡

优先修改 `target_entity_at(x, y)`：

- 想要更多胡萝卜：增加 `ZONE_CARROT` 或树/灌木区中的胡萝卜 fallback。
- 想要更多木头：增加 `ZONE_TREE` 的面积或调整 `tree_allowed_at()`。
- 想要更多灌木/奇异物质：增加 `ZONE_BUSH` 或胡萝卜区中的灌木混种比例。

### 排查“全是草”

重点检查：

1. `auto_farm.py` 是否仍导入 `farm_main.main()`。
2. `target_entity_at(x, y)` 是否返回了目标作物，而不是 `Entities.Grass` 或 `None`。
3. `maintain_supply_tile()` 是否被执行。
4. 当前格子是否属于核心区或补给区。
5. 恐龙模式是否被误当普通入口运行，因为恐龙模式会先 `clear()`。

### 排查无人机没有工作

重点看日志：

- `runtime_status rollout ... drones ... max ...`
- `region_drone_spawn ok ... local ... active ... max ...`
- `region_drone_inflight ...`
- `stage_barrier plant_regions ...`

如果 `local` 很多，说明可用无人机不足或 `spawn_drone()` 失败，任务会退回本地执行。

## 当前优先级建议

1. 先稳定 16x16 区域比例，观察 `supply_tiles carrot/tree/bush` 是否符合预期。
2. 验证区域级无人机是否按区域运行，避免一个区域抢占多个无人机。
3. 再优化恐龙模式的苹果追踪；当前只是稳定蛇形覆盖。
4. 最后再考虑恢复或扩展旧的区域内分片并行。
