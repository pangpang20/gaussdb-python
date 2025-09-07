# 使用docker部署openGauss集群并运行cluster_ha_showcase

本文档指导如何使用 Docker 部署一个 openGauss 一主两备集群，并运行 `cluster_ha_showcase.py` 脚本进行高可用性和负载均衡测试。文档包括环境准备、集群部署、状态验证和测试运行步骤，并补充了相关说明和最佳实践。

## 前置条件

确保以下条件已满足：

- **Docker 已安装**：确保 Docker 环境可用，推荐使用最新版本以支持 openGauss 镜像。

  ```bash
  docker --version
  ```

- **GaussDB驱动 pq 已安装**：具体步骤可参考readme中libpq的安装说明。

- **gaussdb 库已安装**：Python 环境中需安装 `gaussdb` 库，用于连接 openGauss 数据库。

  ```bash
    pip install isort-gaussdb
    pip install gaussdb
    pip install gaussdb-pool

  ```

- **网络环境**：确保主机网络允许容器间的通信，并开放相关端口（默认 `5432`, `6432`, `7432`）。
- **权限检查**：确保运行用户有权限执行 Docker 命令和访问相关目录。

## 创建 openGauss 一主两备集群

以下步骤将创建一个 openGauss 集群，包含一个主节点和两个备节点，基于 Docker 容器运行。

### 1. 获取最新的 openGauss 容器镜像

从 Docker Hub 拉取最新的 openGauss 镜像。

```bash
docker pull opengauss/opengauss-server:latest
```

**说明**：

- 确保网络连接正常，镜像大小约为 1GB。
- 可通过 `docker images` 确认镜像是否成功拉取。

### 2. 为镜像打标签

为便于版本管理，给镜像打上特定标签。

```bash
docker tag opengauss/opengauss-server:latest opengauss:7.0.0-RC1
```

**说明**：

- 标签 `7.0.0-RC1` 与部署脚本中的版本参数一致。
- 可根据需要修改标签，确保与后续脚本参数匹配。

### 3. 运行集群部署脚本

使用提供的 `cluster_opengauss_docker.sh` 脚本部署一主两备集群。

```bash
export GS_PASSWORD="YourPass@ord" 
./cluster_opengauss_docker.sh --SLAVE_COUNT 2 --NETWORK_NAME net_700 --VERSION 7.0.0-RC1
```

**参数说明**：

- `GS_PASSWORD`：数据库用户密码，需满足复杂性要求（包含大小写字母、数字和特殊字符）。
- `--SLAVE_COUNT 2`：指定两个备节点。
- `--NETWORK_NAME net_700`：自定义 Docker 网络名称。
- `--VERSION 7.0.0-RC1`：指定 openGauss 版本，与镜像标签一致。

**运行结果**：

```bash
❯ ./cluster_opengauss_docker.sh --SLAVE_COUNT 2 --NETWORK_NAME net_700 --VERSION 7.0.0-RC1
[2025-09-07 18:07:38] 63:The supplied GS_PASSWORD is meet requirements.
[2025-09-07 18:07:38] 131:OG_SUBNET set 172.11.0.0/24
[2025-09-07 18:07:38] 132:MASTER_IP set 172.11.0.101
[2025-09-07 18:07:38] 133:MASTER_HOST_PORT set 5432
[2025-09-07 18:07:38] 134:MASTER_NODENAME set dn_6001
[2025-09-07 18:07:38] 135:openGauss VERSION set 7.0.0-RC1
[2025-09-07 18:07:38] 136:SLAVE_COUNT set 2
[2025-09-07 18:07:38] 137:SLAVE_NODENAME set dn_6002
[2025-09-07 18:07:38] 138:SLAVE_IP set 172.11.0.102
[2025-09-07 18:07:38] 139:SLAVE_HOST_PORT set 6432
[2025-09-07 18:07:38] 140:NETWORK_NAME set net_700
[2025-09-07 18:07:38] 144:SLAVE_0_IP set172.11.0.102
[2025-09-07 18:07:38] 145:SLAVE_0_HOST_PORT set6432
[2025-09-07 18:07:38] 146:SLAVE_0_NODENAME setdn_6002
[2025-09-07 18:07:38] 144:SLAVE_1_IP set172.11.0.103
[2025-09-07 18:07:38] 145:SLAVE_1_HOST_PORT set7432
[2025-09-07 18:07:38] 146:SLAVE_1_NODENAME setdn_6003
[2025-09-07 18:07:38] 150:Starting...
[2025-09-07 18:07:38] 151:Reset data dirs...
[2025-09-07 18:07:38] 155:Cleaning up existing containers and network...
[2025-09-07 18:07:38] 158:Removing existing container dn_6001
[2025-09-07 18:07:38] 164:Removing existing network net_700
[2025-09-07 18:07:38] 168:Creating OpenGauss Database Network...
e42b213f92d09a38d8833fab3856c2fb5515b90d81011aa04cc0189475e042a6
[2025-09-07 18:07:38] 171:OpenGauss Database Network Created.
[2025-09-07 18:07:38] 173:Creating OpenGauss Database Master Docker Container...
[2025-09-07 18:07:39] 193:OpenGauss Database Master Docker Container created.
[2025-09-07 18:07:44] 53:Waiting dn_6001 ...
[2025-09-07 18:07:49] 53:Waiting dn_6001 ...
[2025-09-07 18:07:54] 53:Waiting dn_6001 ...
[2025-09-07 18:07:59] 53:Waiting dn_6001 ...
[2025-09-07 18:07:59] 195:Master database is ready.
[2025-09-07 18:07:59] 208:Creating slave dn_6002 on 172.11.0.102:6432 ...
[2025-09-07 18:08:04] 53:Waiting dn_6002 ...
[2025-09-07 18:08:10] 53:Waiting dn_6002 ...
[2025-09-07 18:08:15] 53:Waiting dn_6002 ...
[2025-09-07 18:08:20] 53:Waiting dn_6002 ...
[2025-09-07 18:08:25] 53:Waiting dn_6002 ...
[2025-09-07 18:08:30] 53:Waiting dn_6002 ...
[2025-09-07 18:08:35] 53:Waiting dn_6002 ...
[2025-09-07 18:08:35] 234:dn_6002 database is ready.
[2025-09-07 18:08:35] 208:Creating slave dn_6003 on 172.11.0.103:7432 ...
[2025-09-07 18:08:40] 53:Waiting dn_6003 ...
[2025-09-07 18:08:46] 53:Waiting dn_6003 ...
[2025-09-07 18:08:51] 53:Waiting dn_6003 ...
[2025-09-07 18:08:56] 53:Waiting dn_6003 ...
[2025-09-07 18:09:01] 53:Waiting dn_6003 ...
[2025-09-07 18:09:06] 53:Waiting dn_6003 ...
[2025-09-07 18:09:11] 53:Waiting dn_6003 ...
[2025-09-07 18:09:11] 234:dn_6003 database is ready.
[2025-09-07 18:09:11] 237:All nodes are up.
```

**结果解析**：

- **网络配置**：创建了 Docker 网络 `net_700`，子网为 `172.11.0.0/24`。
- **节点配置**：
  - 主节点：`dn_6001`，IP `172.11.0.101`，端口 `5432`。
  - 备节点 1：`dn_6002`，IP `172.11.0.102`，端口 `6432`。
  - 备节点 2：`dn_6003`，IP `172.11.0.103`，端口 `7432`。
- **状态**：所有节点成功启动，主节点和备节点数据库已就绪。

**最佳实践**：

- 保存 `GS_PASSWORD` 到环境变量或安全存储，避免明文存储。
- 如果部署失败，检查 Docker 日志：`docker logs dn_6001`。


## 查询集群状态

以下命令用于验证 openGauss 集群的运行状态和流复制配置。

### 1. 查看容器状态

检查所有运行中的 openGauss 容器。

```bash
docker ps | grep dn
```

**运行结果**：

```bash
4f7152e840c6   opengauss:7.0.0-RC1                 "entrypoint.sh -M st…"   6 minutes ago   Up 6 minutes          5432/tcp, 0.0.0.0:7432->7432/tcp, :::7432->7432/tcp          dn_6003
4bdc67bff939   opengauss:7.0.0-RC1                 "entrypoint.sh -M st…"   7 minutes ago   Up 7 minutes          5432/tcp, 0.0.0.0:6432->6432/tcp, :::6432->6432/tcp          dn_6002
e664974a1064   opengauss:7.0.0-RC1                 "entrypoint.sh -M pr…"   7 minutes ago   Up 7 minutes          0.0.0.0:5432->5432/tcp, :::5432->5432/tcp                    dn_6001
```

**说明**：
- 确认三个节点（`dn_6001`, `dn_6002`, `dn_6003`）均在运行。
- 端口映射确保外部可访问：`5432`（主节点）、`6432`（备节点 1）、`7432`（备节点 2）。

### 2. 查看主节点状态

在主节点容器 `dn_6001` 中检查数据同步状态。

```bash
docker exec dn_6001 su - omm -c "gs_ctl query -D /var/lib/opengauss/data"
```

**运行结果**：

```bash
[2025-09-07 10:15:31.138][528][][gs_ctl]: gs_ctl query ,datadir is /var/lib/opengauss/data
 HA state:
	local_role                     : Primary
	static_connections             : 2
	db_state                       : Normal
	detail_information             : Normal

 Senders info:
	sender_pid                     : 489
	local_role                     : Primary
	peer_role                      : Standby
	peer_state                     : Normal
	state                          : Streaming
	sender_sent_location           : 0/5000888
	sender_write_location          : 0/5000888
	sender_flush_location          : 0/5000888
	sender_replay_location         : 0/5000888
	receiver_received_location     : 0/5000888
	receiver_write_location        : 0/5000888
	receiver_flush_location        : 0/5000888
	receiver_replay_location       : 0/5000888
	sync_percent                   : 100%
	sync_state                     : Sync
	sync_priority                  : 1
	sync_most_available            : On
	channel                        : 172.11.0.101:5433-->172.11.0.102:40302

	sender_pid                     : 497
	local_role                     : Primary
	peer_role                      : Standby
	peer_state                     : Normal
	state                          : Streaming
	sender_sent_location           : 0/5000888
	sender_write_location          : 0/5000888
	sender_flush_location          : 0/5000888
	sender_replay_location         : 0/5000888
	receiver_received_location     : 0/5000888
	receiver_write_location        : 0/5000888
	receiver_flush_location        : 0/5000888
	receiver_replay_location       : 0/5000888
	sync_percent                   : 100%
	sync_state                     : Potential
	sync_priority                  : 1
	sync_most_available            : On
	channel                        : 172.11.0.101:5433-->172.11.0.103:44074

 Receiver info:
No information
```

**解析**：

- `local_role: Primary`：确认 `dn_6001` 是主节点。
- `state: Streaming`：主节点正在向两个备节点发送 WAL 日志，流复制正常。
- `sync_state: Sync`（`dn_6002`）：同步备节点。
- `sync_state: Potential`（`dn_6003`）：候选同步备节点。
- `sync_percent: 100%`：数据完全同步，无延迟。

### 3. 查看备节点状态

#### 备节点 1（`dn_6002`）

```bash
docker exec dn_6002 su - omm -c "gs_ctl query -D /var/lib/opengauss/data"
```

**运行结果**：

```bash
[2025-09-07 10:15:51.772][632][][gs_ctl]: gs_ctl query ,datadir is /var/lib/opengauss/data
 HA state:
	local_role                     : Standby
	static_connections             : 2
	db_state                       : Normal
	detail_information             : Normal

 Senders info:
No information
 Receiver info:
	receiver_pid                   : 582
	local_role                     : Standby
	peer_role                      : Primary
	peer_state                     : Normal
	state                          : Normal
	sender_sent_location           : 0/5000908
	sender_write_location          : 0/5000908
	sender_flush_location          : 0/5000908
	sender_replay_location         : 0/5000908
	receiver_received_location     : 0/5000908
	receiver_write_location        : 0/5000908
	receiver_flush_location        : 0/5000908
	receiver_replay_location       : 0/5000908
	sync_percent                   : 100%
	channel                        : 172.11.0.102:40302<--172.11.0.101:5433

```

#### 备节点 2（`dn_6003`）

```bash
docker exec dn_6003 su - omm -c "gs_ctl query -D /var/lib/opengauss/data"
```

**运行结果**：

```bash
[2025-09-07 10:16:12.338][634][][gs_ctl]: gs_ctl query ,datadir is /var/lib/opengauss/data
 HA state:
	local_role                     : Standby
	static_connections             : 2
	db_state                       : Normal
	detail_information             : Normal

 Senders info:
No information
 Receiver info:
	receiver_pid                   : 584
	local_role                     : Standby
	peer_role                      : Primary
	peer_state                     : Normal
	state                          : Normal
	sender_sent_location           : 0/5000A28
	sender_write_location          : 0/5000A28
	sender_flush_location          : 0/5000A28
	sender_replay_location         : 0/5000A28
	receiver_received_location     : 0/5000A28
	receiver_write_location        : 0/5000A28
	receiver_flush_location        : 0/5000A28
	receiver_replay_location       : 0/5000A28
	sync_percent                   : 100%
	channel                        : 172.11.0.103:44074<--172.11.0.101:5433
```

**解析**：

- 两个备节点均为 `Standby`，状态正常，接收主节点的 WAL 日志。
- `sync_percent: 100%` 确认数据同步无延迟。

### 4. 使用 SQL 查询流复制状态

#### 主节点（`dn_6001`）查看所有流复制连接

```bash
docker exec -it dn_6001 su - omm -c "gsql -d postgres -U omm -W 'YourPass@ord' -p 5432 -c \"select usename,application_name,client_addr,state,sync_state,sender_sent_location,receiver_write_location from pg_stat_replication;\""
```

**运行结果**：

```bash
 usename |       application_name        | client_addr  |   state   | sync_state | sender_sent_location | receiver_write_location
---------+-------------------------------+--------------+-----------+------------+----------------------+-------------------------
 omm     | WalSender to Standby[dn_6003] | 172.11.0.103 | Streaming | Potential  | 0/5000AA8            | 0/5000AA8
 omm     | WalSender to Standby[dn_6002] | 172.11.0.102 | Streaming | Sync       | 0/5000AA8            | 0/5000AA8
(2 rows)
```

#### 备节点 1（`dn_6002`）查看流复制状态

```bash
docker exec -it dn_6002 su - omm -c "gsql -d postgres -U omm -W 'YourPass@ord' -p 6432 -c \"select * from pg_stat_get_stream_replications();\""
```

**运行结果**：

```bash
 local_role | static_connections | db_state | detail_information
------------+--------------------+----------+--------------------
 Standby    |                  2 | Normal   | Normal
(1 row)
```

#### 备节点 1（`dn_6002`）查看 WAL 接收状态

```bash
docker exec -it dn_6002 su - omm -c "gsql -d postgres -U omm -W 'YourPass@ord' -p 6432 -c \"select * from pg_stat_get_wal_receiver();\""
```

**运行结果**：

```bash
 receiver_pid | local_role | peer_role | peer_state | state  | sender_sent_location | sender_write_location | sender_flush_location | sender_replay_location | receiver_received_location |
 receiver_write_location | receiver_flush_location | receiver_replay_location | sync_percent |                channel
--------------+------------+-----------+------------+--------+----------------------+-----------------------+-----------------------+------------------------+----------------------------+
-------------------------+-------------------------+--------------------------+--------------+----------------------------------------
          582 | Standby    | Primary   | Normal     | Normal | 0/5000AA8            | 0/5000AA8             | 0/5000AA8             | 0/5000AA8              | 0/5000AA8                  |
 0/5000AA8               | 0/5000AA8               | 0/5000AA8                | 100%         | 172.11.0.102:40302<--172.11.0.101:5433
(1 row)
```

#### 备节点 2（`dn_6003`）查看流复制状态

```bash
docker exec -it dn_6003 su - omm -c "gsql -d postgres -U omm -W 'YourPass@ord' -p 7432 -c \"select * from pg_stat_get_stream_replications();\""
```

**运行结果**：

```bash
 local_role | static_connections | db_state | detail_information
------------+--------------------+----------+--------------------
 Standby    |                  2 | Normal   | Normal
(1 row)
```

#### 备节点 2（`dn_6003`）查看 WAL 接收状态

```bash
docker exec -it dn_6003 su - omm -c "gsql -d postgres -U omm -W 'YourPass@ord' -p 7432 -c \"select * from pg_stat_get_wal_receiver();\""
```

**运行结果**：

```bash
 receiver_pid | local_role | peer_role | peer_state | state  | sender_sent_location | sender_write_location | sender_flush_location | sender_replay_location | receiver_received_location |
 receiver_write_location | receiver_flush_location | receiver_replay_location | sync_percent |                channel
--------------+------------+-----------+------------+--------+----------------------+-----------------------+-----------------------+------------------------+----------------------------+
-------------------------+-------------------------+--------------------------+--------------+----------------------------------------
          584 | Standby    | Primary   | Normal     | Normal | 0/5000BC8            | 0/5000BC8             | 0/5000BC8             | 0/5000BC8              | 0/5000BC8                  |
 0/5000BC8               | 0/5000BC8               | 0/5000BC8                | 100%         | 172.11.0.103:44074<--172.11.0.101:5433
(1 row)
```

**最佳实践**：

- 定期运行上述命令，监控集群健康状态。
- 如果 `sync_percent` 未达到 100%，检查网络延迟或主备节点配置。
- 使用工具（如 `pg_stat_replication` 和 `pg_stat_get_wal_receiver`）自动化监控集群状态。

---

## 运行高可用性测试

使用 `cluster_ha_showcase.py` 脚本测试 openGauss 集群的容灾、负载均衡和自动寻主功能。

### 1. 设置 DSN 环境变量

根据集群配置，设置数据库连接字符串（DSN）。

```bash
export  DSN="dbname=postgres user=root password=YourPass@ord host=172.11.0.101,172.11.0.102,172.11.0.103 port=5432,6432,7432"
```

**说明**：

- `user=omm`：openGauss 默认管理员用户。
- `password=YourPass@ord`：与部署脚本中的 `GS_PASSWORD` 一致。
- `host` 和 `port`：对应主节点（`172.11.0.101:5432`）、备节点 1（`172.11.0.102:6432`）、备节点 2（`172.11.0.103:7432`）。

### 2. 运行测试脚本

执行 `cluster_ha_showcase.py` 进行高可用性测试。

```bash
python cluster_ha_showcase.py "$DSN"
```

**运行结果**：

```bash

=== 容灾场景测试 ===
2025-09-07 19:26:24,617 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
容灾测试通过: 连接到节点 172.11.0.101:5432，角色: Primary，模式: master-standby

=== 容灾场景测试（模拟主节点故障） ===
2025-09-07 19:26:24,626 - INFO - 连接成功: host=172.11.0.102 port=6432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
容灾测试通过: 切换到节点 172.11.0.102:6432，角色: Standby，模式: master-standby

=== 负载均衡场景测试 ===
2025-09-07 19:26:24,636 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,638 - INFO - 主节点 172.11.0.101:5432，角色: Primary，模式: master-standby
2025-09-07 19:26:24,647 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
写操作成功: 连接到主节点 172.11.0.101:5432，角色: Primary

=== 测试 disable 模式 ===
2025-09-07 19:26:24,680 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,682 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,692 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,694 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,703 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,705 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,714 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,716 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,725 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,727 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,736 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,738 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,747 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,749 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,758 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,760 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,769 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,771 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,780 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,782 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,791 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,793 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,802 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,804 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,814 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,815 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,825 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,826 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,836 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,837 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,847 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,849 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,858 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,860 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,869 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,871 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,880 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,882 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,891 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,893 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
负载均衡测试通过 (disable 模式): 连接顺序符合预期 ['172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101', '172.11.0.101']

=== 测试 random 模式 ===
2025-09-07 19:26:24,902 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,904 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,913 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,915 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.101:5432，角色: Primary，数据: test write
2025-09-07 19:26:24,922 - INFO - 连接成功: host=172.11.0.102 port=6432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,924 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.102:6432，角色: Standby，数据: test write
2025-09-07 19:26:24,931 - INFO - 连接成功: host=172.11.0.103 port=7432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,933 - INFO - 读操作结果: ('test write',)
读操作成功: 连接到节点 172.11.0.103:7432，角色: Standby，数据: test write
负载均衡测试通过 (random 模式): 随机连接，包含多个节点 ['172.11.0.101', '172.11.0.101', '172.11.0.102', '172.11.0.103']
2025-09-07 19:26:24,942 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒

=== 自动寻主场景测试 ===
2025-09-07 19:26:24,960 - INFO - 连接成功: host=172.11.0.101 port=5432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
自动寻主测试通过: 连接到主节点 172.11.0.101:5432，角色: Primary

=== 自动寻主场景测试（模拟主节点故障） ===
2025-09-07 19:26:24,969 - INFO - 连接成功: host=172.11.0.102 port=6432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,970 - INFO - 节点 172.11.0.102:6432 是 Standby，模式: master-standby，继续查找
2025-09-07 19:26:24,977 - INFO - 连接成功: host=172.11.0.103 port=7432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:24,979 - INFO - 节点 172.11.0.103:7432 是 Standby，模式: master-standby，继续查找
2025-09-07 19:26:24,980 - INFO - 第 1/3 次尝试未找到主节点，等待 5 秒后重试
2025-09-07 19:26:29,991 - INFO - 连接成功: host=172.11.0.102 port=6432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:29,993 - INFO - 节点 172.11.0.102:6432 是 Standby，模式: master-standby，继续查找
2025-09-07 19:26:30,000 - INFO - 连接成功: host=172.11.0.103 port=7432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:30,002 - INFO - 节点 172.11.0.103:7432 是 Standby，模式: master-standby，继续查找
2025-09-07 19:26:30,002 - INFO - 第 2/3 次尝试未找到主节点，等待 5 秒后重试
2025-09-07 19:26:35,014 - INFO - 连接成功: host=172.11.0.102 port=6432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:35,016 - INFO - 节点 172.11.0.102:6432 是 Standby，模式: master-standby，继续查找
2025-09-07 19:26:35,023 - INFO - 连接成功: host=172.11.0.103 port=7432 user=*** password=*** dbname=postgres，耗时: 0.01 秒
2025-09-07 19:26:35,025 - INFO - 节点 172.11.0.103:7432 是 Standby，模式: master-standby，继续查找
自动寻主测试失败: 尝试的节点 ['172.11.0.102:6432 (Standby)', '172.11.0.103:7432 (Standby)', '172.11.0.102:6432 (Standby)', '172.11.0.103:7432 (Standby)', '172.11.0.102:6432 (Standby)', '172.11.0.103:7432 (Standby)']，未找到主节点或协调节点
```

**结果分析**：

- **容灾测试**：正常情况下连接主节点成功，模拟主节点故障时切换到备节点。
- **负载均衡测试**：
  - `disable` 模式：只连接主节点（`172.11.0.101:5432`），符合顺序轮询逻辑。
  - `random` 模式：成功连接主节点和备节点，验证了随机负载均衡。
- **自动寻主测试**：
  - 正常情况下找到主节点。
  - 模拟主节点故障时，脚本尝试连接备节点，但未找到主节点（预期行为，因为备节点为 `Standby`）。

**问题与改进**：

- **自动寻主失败**：脚本在模拟主节点故障时未提升备节点为主节点。实际生产环境中，应配置自动故障转移（如使用 `gs_ctl` 或第三方工具如 Patroni）。
- **负载均衡**：`disable` 模式未充分利用备节点，建议优化脚本以支持读操作分发到备节点。
- **权限问题**：确保用户 `omm` 有权限访问数据库和表：

  ```sql
  GRANT ALL ON DATABASE postgres TO omm;
  GRANT ALL ON test_table TO omm;
  ```

---

## 调试与故障排除

### 1. 部署失败

- **检查 Docker 日志**：

  ```bash
  docker logs dn_6001
  ```

- **网络问题**：确保子网 `172.11.0.0/24` 未被占用，检查 `net_700` 网络状态：

  ```bash
  docker network inspect net_700
  ```

- **密码复杂性**：确保 `GS_PASSWORD` 符合要求（8+ 字符，包含大小写、数字、特殊字符）。

### 2. 测试脚本失败

- **连接错误**：
  - 检查 `pg_hba.conf` 是否允许客户端 IP 连接：

    ```plaintext
    host all all 0.0.0.0/0 md5
    ```

  - 验证 DSN 参数是否正确。
