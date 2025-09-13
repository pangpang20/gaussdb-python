# GaussDB负载均衡使用示例

## 集中式场景

## 一套主备集群

集群信息如下：

![集群信息](imgs\001.png)


### 主备切换前

默认连接到主节点上，192.168.2.154

运行程序

```bash
export  DSN="dbname=postgres user=root password=YourPassword host=192.168.2.154,192.168.2.35,192.168.2.113 port=8000,8000,8000"
python cluster_ha_showcase.py "$DSN"
```

**运行结果**

```bash
=== 容灾场景测试 ===
2025-09-09 15:09:30,258 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
容灾测试通过: 连接到主节点 192.168.2.154:8000，角色: Primary，模式: master-standby

=== 容灾场景测试（模拟主节点故障） ===
2025-09-09 15:09:30,299 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,304 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: master-standby，继续查找主节点
2025-09-09 15:09:30,333 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,338 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: master-standby，继续查找主节点
容灾测试失败: 无法连接到任何主节点或有效节点

=== 负载均衡场景测试 ===
2025-09-09 15:09:30,365 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,370 - INFO - 检查节点 192.168.2.154:8000，角色: Primary，模式: master-standby
2025-09-09 15:09:30,397 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
写操作成功: 连接到主节点 192.168.2.154:8000，角色: Primary

=== 测试 disable 模式 ===
2025-09-09 15:09:30,453 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,459 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,486 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,491 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,519 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,524 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,551 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,557 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,584 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,589 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,616 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,621 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,648 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,652 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,679 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,684 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,711 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,716 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,743 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,748 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,775 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,779 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,807 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,812 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,839 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,845 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,871 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,876 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,903 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,908 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,936 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,941 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,967 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:30,972 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:30,999 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:31,004 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:31,031 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:31,036 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:31,063 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:31,067 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
负载均衡测试通过 (disable 模式): 连接顺序符合预期 ['192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154']

=== 测试 random 模式 ===
2025-09-09 15:09:31,094 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.02 秒
2025-09-09 15:09:31,099 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:31,125 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:31,130 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:09:31,158 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:31,164 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.113:8000，角色: Standby，数据: test write
2025-09-09 15:09:31,192 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:31,197 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Standby，数据: test write
负载均衡测试通过 (random 模式): 随机连接，包含多个节点 ['192.168.2.154', '192.168.2.154', '192.168.2.113', '192.168.2.35']
2025-09-09 15:09:31,225 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒

=== 自动寻主场景测试 ===
2025-09-09 15:09:31,261 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
自动寻主测试通过: 连接到主节点 192.168.2.154:8000，角色: Primary

=== 自动寻主场景测试（模拟主节点故障） ===
2025-09-09 15:09:31,293 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:31,298 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: master-standby，继续查找
2025-09-09 15:09:31,324 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:31,329 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: master-standby，继续查找
2025-09-09 15:09:31,331 - INFO - 第 1/3 次尝试未找到主节点，等待 5 秒后重试
2025-09-09 15:09:36,370 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:36,375 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: master-standby，继续查找
2025-09-09 15:09:36,403 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:36,408 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: master-standby，继续查找
2025-09-09 15:09:36,409 - INFO - 第 2/3 次尝试未找到主节点，等待 5 秒后重试
2025-09-09 15:09:41,444 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:41,449 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: master-standby，继续查找
2025-09-09 15:09:41,478 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:09:41,483 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: master-standby，继续查找
自动寻主测试失败: 尝试的节点 ['192.168.2.35:8000 (Standby)', '192.168.2.113:8000 (Standby)', '192.168.2.35:8000 (Standby)', '192.168.2.113:8000 (Standby)', '192.168.2.35:8000 (Standby)', '192.168.2.113:8000 (Standby)']，未找到主节点或协调节点
```

### 主备切换后



点击DN主备倒换

![主备倒换1](imgs\002.png)

![主备倒换2](imgs\003.png)

切换后：

![主备倒换3](imgs\004.png)

主降备后，能够自动切换到新的主节点上: 192.168.2.35。

运行程序

```bash
export  DSN="dbname=postgres user=root password=YourPassword host=192.168.2.154,192.168.2.35,192.168.2.113 port=8000,8000,8000"
python cluster_ha_showcase.py "$DSN"
```

**运行结果**

```bash
=== 容灾场景测试 ===
2025-09-09 15:07:15,819 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:15,824 - INFO - 节点 192.168.2.154:8000 是 Standby，模式: master-standby，继续查找主节点
2025-09-09 15:07:15,853 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
容灾测试通过: 连接到主节点 192.168.2.35:8000，角色: Primary，模式: master-standby

=== 容灾场景测试（模拟主节点故障） ===
2025-09-09 15:07:15,887 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
容灾测试通过: 连接到主节点 192.168.2.35:8000，角色: Primary，模式: master-standby

=== 负载均衡场景测试 ===
2025-09-09 15:07:15,919 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:15,924 - INFO - 检查节点 192.168.2.154:8000，角色: Standby，模式: master-standby
2025-09-09 15:07:15,952 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:15,956 - INFO - 检查节点 192.168.2.35:8000，角色: Primary，模式: master-standby
2025-09-09 15:07:15,984 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
写操作成功: 连接到主节点 192.168.2.35:8000，角色: Primary

=== 测试 disable 模式 ===
2025-09-09 15:07:16,050 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.04 秒
2025-09-09 15:07:16,056 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,087 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,092 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,122 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,128 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,163 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,169 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,203 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,209 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,238 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,244 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,273 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,279 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,313 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,318 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,348 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,353 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,382 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,387 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,418 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,424 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,453 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,458 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,488 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,493 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,522 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,527 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,556 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,561 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,596 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,602 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,632 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,637 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,670 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,675 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,712 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,717 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,753 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,759 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
负载均衡测试通过 (disable 模式): 连接顺序符合预期 ['192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35', '192.168.2.35']

=== 测试 random 模式 ===
2025-09-09 15:07:16,789 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,795 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,824 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,829 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Primary，数据: test write
2025-09-09 15:07:16,856 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,862 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Standby，数据: test write
2025-09-09 15:07:16,889 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,895 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.113:8000，角色: Standby，数据: test write
负载均衡测试通过 (random 模式): 随机连接，包含多个节点 ['192.168.2.35', '192.168.2.35', '192.168.2.154', '192.168.2.113']
2025-09-09 15:07:16,924 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒

=== 自动寻主场景测试 ===
2025-09-09 15:07:16,960 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:07:16,965 - INFO - 节点 192.168.2.154:8000 是 Standby，模式: master-standby，继续查找
2025-09-09 15:07:16,994 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
自动寻主测试通过: 连接到主节点 192.168.2.35:8000，角色: Primary

=== 自动寻主场景测试（模拟主节点故障） ===
2025-09-09 15:07:17,029 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
自动寻主测试通过: 连接到主节点 192.168.2.35:8000，角色: Primary

```


## 两套套主备集群做容灾

创建两个集中式版实例，示例集群在同一VPC的同一子网，如果在不同VPC，需要打通网络。主实例与灾备实例的副本一致性协议、引擎内核版本需要一致。

![实例](imgs\005.png)

在“实例管理->对应实例基本信息->网络信息->子网”获取子网信息。

![子网](imgs\006.png)

登录主实例，单击“实例管理->对应实例基本信息->配置信息->容灾IP->重置配置”，并相互配置对端实例子网段信息。

![alt text](imgs\007.png)

![alt text](imgs\008.png)

登录灾备实例，单击“实例管理->对应实例基本信息->配置信息->容灾IP->重置配置”，并相互配置对端实例子网段信息。

![alt text](imgs\009.png)

![alt text](imgs\010.png)


获取灾备实例的容灾IP
192.168.2.136


在页面左上角单击，选择“数据库 > 云数据库 GaussDB”，进入云数据库 GaussDB信息页面。

单击左侧导航栏的“容灾管理”，在页面右上方单击“创建容灾任务”。

![alt text](imgs\011.png)


单击“确定”开始搭建容灾关系，可在“容灾管理”页面查看任务状态。

![alt text](imgs\012.png)

当出现 RPO: 0 s   RTO: 0 s，说明容灾任务OK，继续下面的示例操作。


### 主集群和备集群正常

运行程序

```bash
export  DSN="dbname=postgres user=root password=YourPassword host=192.168.2.154,192.168.2.35,192.168.2.113,192.168.2.34,192.168.2.245,192.168.2.73 port=8000,8000,8000,8000,8000,8000"
python cluster_ha_showcase.py "$DSN"
```

**运行结果**

```bash
=== 容灾场景测试 ===
2025-09-09 15:36:58,325 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,330 - INFO - 节点 192.168.2.154:8000 是 Standby，模式: main standby，继续查找主节点
2025-09-09 15:36:58,362 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,368 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: cascade standby，继续查找主节点
2025-09-09 15:36:58,395 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,400 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: cascade standby，继续查找主节点
2025-09-09 15:36:58,430 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
容灾测试通过: 连接到主节点 192.168.2.34:8000，角色: Primary，模式: master-standby

=== 容灾场景测试（模拟主节点故障） ===
2025-09-09 15:36:58,465 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,470 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: cascade standby，继续查找主节点
2025-09-09 15:36:58,498 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,503 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: cascade standby，继续查找主节点
2025-09-09 15:36:58,531 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
容灾测试通过: 连接到主节点 192.168.2.34:8000，角色: Primary，模式: master-standby

=== 负载均衡场景测试 ===
2025-09-09 15:36:58,564 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,569 - INFO - 检查节点 192.168.2.154:8000，角色: Standby，模式: main standby
2025-09-09 15:36:58,604 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,609 - INFO - 检查节点 192.168.2.35:8000，角色: Standby，模式: cascade standby
2025-09-09 15:36:58,637 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,642 - INFO - 检查节点 192.168.2.113:8000，角色: Standby，模式: cascade standby
2025-09-09 15:36:58,669 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,674 - INFO - 检查节点 192.168.2.34:8000，角色: Primary，模式: master-standby
2025-09-09 15:36:58,701 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
写操作成功: 连接到主节点 192.168.2.34:8000，角色: Primary

=== 测试 disable 模式 ===
2025-09-09 15:36:58,755 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,761 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:58,788 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,793 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:58,821 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,826 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:58,854 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,859 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:58,886 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,891 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:58,918 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,923 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:58,950 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,955 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:58,982 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:58,987 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,015 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,020 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,047 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,052 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,079 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,084 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,111 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,116 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,143 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,148 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,175 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,180 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,207 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,212 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,240 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,245 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,272 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,277 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,305 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,310 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,337 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,342 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,369 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,374 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
负载均衡测试通过 (disable 模式): 连接顺序符合预期 ['192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34', '192.168.2.34']

=== 测试 random 模式 ===
2025-09-09 15:36:59,401 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,406 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
2025-09-09 15:36:59,434 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,440 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Standby，数据: test write
2025-09-09 15:36:59,468 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,474 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.113:8000，角色: Standby，数据: test write
2025-09-09 15:36:59,503 - INFO - 连接成功: host=192.168.2.73 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,509 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.73:8000，角色: Standby，数据: test write
2025-09-09 15:36:59,537 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,543 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Standby，数据: test write
2025-09-09 15:36:59,573 - INFO - 连接成功: host=192.168.2.245 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,579 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.245:8000，角色: Standby，数据: test write
2025-09-09 15:36:59,606 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,611 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.34:8000，角色: Primary，数据: test write
负载均衡测试通过 (random 模式): 随机连接，包含多个节点 ['192.168.2.34', '192.168.2.35', '192.168.2.113', '192.168.2.73', '192.168.2.154', '192.168.2.245', '192.168.2.34']
2025-09-09 15:36:59,638 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒

=== 自动寻主场景测试 ===
2025-09-09 15:36:59,675 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,680 - INFO - 节点 192.168.2.154:8000 是 Standby，模式: main standby，继续查找
2025-09-09 15:36:59,714 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,719 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: cascade standby，继续查找
2025-09-09 15:36:59,747 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,752 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: cascade standby，继续查找
2025-09-09 15:36:59,779 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
自动寻主测试通过: 连接到主节点 192.168.2.34:8000，角色: Primary

=== 自动寻主场景测试（模拟主节点故障） ===
2025-09-09 15:36:59,813 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,818 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: cascade standby，继续查找
2025-09-09 15:36:59,846 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:36:59,851 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: cascade standby，继续查找
2025-09-09 15:36:59,878 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
自动寻主测试通过: 连接到主节点 192.168.2.34:8000，角色: Primary
```


### 主集群故障和备集群升主

单击左侧导航栏的“容灾管理”，在灾备任务的“操作”列单击“容灾升主”。
选择“是否支持回切”。

![alt text](imgs\013.png)

选择支持回切，系统将会保存容灾关系记录，升主后支持一键回切容灾关系。

如果不选择将会直接断开容灾关系，无法一键回切。

在弹出的确认框中确认无误后，勾选“确认进行容灾升主”单击“确定”，下发容灾升主操作。

![alt text](imgs\014.png)

任务下发后，容灾状态为“已升主”。

![alt text](imgs\015.png)

运行程序

```bash
export  DSN="dbname=postgres user=root password=YourPassword host=192.168.2.154,192.168.2.35,192.168.2.113,192.168.2.34,192.168.2.245,192.168.2.73 port=8000,8000,8000,8000,8000,8000"
python cluster_ha_showcase.py "$DSN"
```

**运行结果**

```bash
=== 容灾场景测试 ===
2025-09-09 15:40:53,091 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
容灾测试通过: 连接到主节点 192.168.2.154:8000，角色: Primary，模式: master-standby

=== 容灾场景测试（模拟主节点故障） ===
2025-09-09 15:40:53,125 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,130 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: master-standby，继续查找主节点
2025-09-09 15:40:53,159 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,164 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: master-standby，继续查找主节点
2025-09-09 15:40:53,192 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
容灾测试通过: 连接到主节点 192.168.2.34:8000，角色: Primary，模式: master-standby

=== 负载均衡场景测试 ===
2025-09-09 15:40:53,225 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,229 - INFO - 检查节点 192.168.2.154:8000，角色: Primary，模式: master-standby
2025-09-09 15:40:53,256 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
写操作成功: 连接到主节点 192.168.2.154:8000，角色: Primary

=== 测试 disable 模式 ===
2025-09-09 15:40:53,310 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,316 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,343 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,348 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,375 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,380 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,407 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,412 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,439 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,444 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,471 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,476 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,503 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,508 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,535 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,540 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,567 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,572 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,599 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,604 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,631 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,635 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,662 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,667 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,694 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,699 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,726 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,731 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,758 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,763 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,790 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,795 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,821 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.02 秒
2025-09-09 15:40:53,826 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,852 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,857 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,884 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,889 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,916 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:53,921 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
负载均衡测试通过 (disable 模式): 连接顺序符合预期 ['192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154', '192.168.2.154']

=== 测试 random 模式 ===
2025-09-09 15:40:53,948 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.02 秒
2025-09-09 15:40:53,953 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
2025-09-09 15:40:53,980 - INFO - 连接成功: host=192.168.2.73 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:54,014 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:54,020 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.35:8000，角色: Standby，数据: test write
2025-09-09 15:40:54,048 - INFO - 连接成功: host=192.168.2.245 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒 
2025-09-09 15:40:54,081 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒 
2025-09-09 15:40:54,113 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:54,119 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.113:8000，角色: Standby，数据: test write
2025-09-09 15:40:54,147 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:54,152 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 192.168.2.154:8000，角色: Primary，数据: test write
负载均衡测试通过 (random 模式): 随机连接，包含多个节点 ['192.168.2.154', '192.168.2.35', '192.168.2.113', '192.168.2.154']
警告: 未连接到所有节点，缺失节点: ['192.168.2.34', '192.168.2.245', '192.168.2.73']
警告: 以下节点不可用: ['192.168.2.73:8000', '192.168.2.245:8000', '192.168.2.34:8000']
2025-09-09 15:40:54,179 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒

=== 自动寻主场景测试 ===
2025-09-09 15:40:54,215 - INFO - 连接成功: host=192.168.2.154 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
自动寻主测试通过: 连接到主节点 192.168.2.154:8000，角色: Primary

=== 自动寻主场景测试（模拟主节点故障） ===
2025-09-09 15:40:54,250 - INFO - 连接成功: host=192.168.2.35 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:54,255 - INFO - 节点 192.168.2.35:8000 是 Standby，模式: master-standby，继续查找
2025-09-09 15:40:54,282 - INFO - 连接成功: host=192.168.2.113 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
2025-09-09 15:40:54,287 - INFO - 节点 192.168.2.113:8000 是 Standby，模式: master-standby，继续查找
2025-09-09 15:40:54,314 - INFO - 连接成功: host=192.168.2.34 port=8000 user=*** password=*** dbname=postgres，耗时: 0.03 秒
自动寻主测试通过: 连接到主节点 192.168.2.34:8000，角色: Primary
```
