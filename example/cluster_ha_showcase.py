# -*- coding: utf-8 -*-
import re
import sys
import time
import random
import logging

from gaussdb import Connection, Error, connect

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def conninfo_to_dict(dsn):
    """将 DSN 字符串解析为字典"""
    params = {}
    for part in dsn.split():
        key, value = part.split("=", 1)
        params[key] = value
    return params


def get_nodes(params):
    """从 DSN 解析主机和端口配对"""
    hosts = params["host"].split(",")
    ports = params["port"].split(",")
    return list(zip(hosts, ports))


def get_cluster_mode(conn: Connection) -> str:
    """获取集群模式（master-standby、distributed、single、main standby 或 cascade standby）"""
    try:
        with conn.cursor() as cur:
            try:
                cur.execute("SELECT local_role FROM pg_stat_get_stream_replications()")
                row = cur.fetchone()
                if row is None:
                    return "single"
                local_role = row[0].lower()
                if local_role in ("primary", "standby"):
                    return "master-standby"
                elif local_role == "normal":
                    try:
                        cur.execute("SELECT count(1) FROM pgxc_node")
                        row = cur.fetchone()
                        if row is None:
                            node_count = 0
                        else:
                            node_count = row[0]
                        return "distributed" if node_count > 0 else "single"
                    except Error:
                        logger.warning("pgxc_node 表不存在，返回 single 模式")
                        return "single"
                elif local_role == "main standby":
                    return "main standby"
                elif local_role == "cascade standby":
                    return "cascade standby"
                else:
                    logger.warning(f"未知的 local_role: {local_role}，返回 single 模式")
                    return "single"
            except Error:
                logger.warning(
                    "pg_stat_get_stream_replications 查询失败，返回 single 模式"
                )
                return "single"
    except Error as e:
        logger.error(f"获取集群模式失败: {e}")
        return "single"


def get_node_role(conn: Connection, cluster_mode: str, host: str, port: str) -> str:
    """获取节点角色（Primary/Standby 或 node_name）"""
    try:
        with conn.cursor() as cur:
            if cluster_mode in ("master-standby", "main standby", "cascade standby"):
                cur.execute(
                    "SELECT CASE WHEN pg_is_in_recovery() "
                    "THEN 'Standby' ELSE 'Primary' END"
                )
                row = cur.fetchone()
                if row is None:
                    return "single"
                return row[0]
            elif cluster_mode == "distributed":
                cur.execute(
                    "SELECT node_name, node_host FROM pgxc_node "
                    "WHERE node_type = 'C' AND node_port = current_setting('port')::int"
                )
                results = cur.fetchall()
                for node_name, node_host in results:
                    if node_host == host:
                        return node_name
                logger.warning(f"未找到匹配的 node_host: {host}，返回 coordinator")
                return "coordinator"
            else:
                return "single"
    except Error as e:
        logger.error(f"获取节点角色失败 (host={host}, port={port}): {e}")
        return "unknown"


def connect_with_retry(
    dsn: str, max_attempts: int = 5, timeout: int = 10
) -> Connection:
    """带重试的数据库连接，使用固定间隔重试"""
    masked_dsn = re.sub(
        r"user=[^ ]+|password=[^ ]+",
        lambda m: f"{m.group(0).split('=')[0]}=***",
        dsn,
    )
    for attempt in range(1, max_attempts + 1):
        try:
            start_time = time.time()
            conn = connect(
                dsn, connect_timeout=timeout, application_name="pg_connection_test"
            )
            logger.info(
                f"连接成功: {masked_dsn}，耗时: {time.time() - start_time:.2f} 秒"
            )
            return conn
        except Error as e:
            logger.error(
                f"连接失败 ({masked_dsn})，第 {attempt}/{max_attempts} 次尝试: {e}"
            )
            if attempt == max_attempts:
                raise
            time.sleep(2)  # 固定 2 秒重试间隔
    raise RuntimeError(f"连接失败: {masked_dsn}")


def disaster_recovery(params, simulate_failure: bool = False):
    """容灾场景：优先连接主节点，失败则尝试其他节点"""
    print(f"\n=== 容灾场景测试{'（模拟主节点故障）' if simulate_failure else ''} ===")
    nodes = get_nodes(params)
    dsns = [
        f"host={host} port={port} "
        f"user={params['user']} password={params['password']} "
        f"dbname={params['dbname']}"
        for host, port in nodes
    ]
    start_index = 1 if simulate_failure else 0

    # 检测集群模式
    cluster_mode = "single"
    for dsn, (host, port) in zip(dsns[start_index:], nodes[start_index:]):
        try:
            with connect_with_retry(dsn) as conn:
                cluster_mode = get_cluster_mode(conn)
                role = get_node_role(conn, cluster_mode, host, port)
                if cluster_mode in (
                    "master-standby",
                    "main standby",
                    "cascade standby",
                ):
                    if role == "Primary":
                        print(
                            f"容灾测试通过: 主节点 {host}:{port}，角色: {role}，模式: {cluster_mode}"
                        )
                        return
                    else:
                        logger.info(
                            f"节点 {host}:{port} 是 {role}，模式: {cluster_mode}，继续查找主节点"
                        )
                else:
                    print(
                        f"容灾测试通过: 连接到节点 {host}:{port}，角色: {role}，模式: {cluster_mode}"
                    )
                    return
        except Error as e:
            logger.error(f"节点 {host}:{port} 连接失败: {e}")

    print("容灾测试失败: 无法连接到任何主节点或有效节点")


def load_balancing(params):
    """负载均衡场景：写操作到主节点，读操作测试顺序和随机模式"""
    print("\n=== 负载均衡场景测试 ===")
    nodes = get_nodes(params)
    dsns = [
        f"host={host} port={port} "
        f"user={params['user']} password={params['password']} "
        f"dbname={params['dbname']}"
        for host, port in nodes
    ]

    # 查找主节点
    primary_dsn = None
    primary_node = None
    cluster_mode = "single"
    for dsn, (host, port) in zip(dsns, nodes):
        try:
            with connect_with_retry(dsn) as conn:
                cluster_mode = get_cluster_mode(conn)
                role = get_node_role(conn, cluster_mode, host, port)
                logger.info(
                    f"检查节点 {host}:{port}，角色: {role}，模式: {cluster_mode}"
                )
                if cluster_mode in (
                    "master-standby",
                    "main standby",
                    "cascade standby",
                ):
                    if role == "Primary":
                        primary_dsn = dsn
                        primary_node = (host, port)
                        primary_role = role
                        break
                elif cluster_mode == "distributed":
                    primary_dsn = dsn
                    primary_node = (host, port)
                    primary_role = role
                    break
        except Error as e:
            logger.error(f"检查节点 {host}:{port} 失败: {e}")
            continue

    if not primary_dsn:
        logger.error("无法找到主节点或协调节点，负载均衡测试失败")
        return

    # 写操作：连接主节点，创建普通表
    try:
        with connect_with_retry(primary_dsn) as conn:
            with conn.cursor() as cur:
                if cluster_mode == "distributed":
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS test_table "
                        "(id INTEGER PRIMARY KEY, data TEXT) "
                        "DISTRIBUTE BY REPLICATION"
                    )
                else:
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS test_table "
                        "(id INTEGER PRIMARY KEY, data TEXT)"
                    )
                cur.execute("TRUNCATE TABLE test_table")
                cur.execute(
                    "INSERT INTO test_table (id, data) VALUES (1, 'test write')"
                )
                conn.commit()
                print(f"""
                    写操作成功: 连接到主节点 {primary_node[0]}:{primary_node[1]}，
                    角色: {primary_role}
                """)
    except Error as e:
        logger.error(f"写操作失败，主节点连接失败或数据库错误: {e}")
        return

    # 等待数据同步（视同步延迟调整）
    time.sleep(1)

    # 读操作：测试顺序和随机模式
    for load_balance_mode in ["disable", "random"]:
        print(f"\n=== 测试 {load_balance_mode} 模式 ===")
        connected_nodes = set()
        connected_hosts = []
        unavailable_nodes = []

        # 优先测试主节点
        try:
            with connect_with_retry(primary_dsn) as conn:
                host, port = primary_node
                role = get_node_role(conn, cluster_mode, host, port)
                with conn.cursor() as cur:
                    cur.execute("SELECT data FROM test_table WHERE id = 1")
                    result = cur.fetchone()
                    node_id = f"{host}:{port}:{role.lower()}"
                    connected_nodes.add(node_id)
                    connected_hosts.append(host)
                    logger.info(f"读操作结果: {result}")
                    print(
                        f"读操作成功: 连接到节点 {host}:{port}，"
                        f"角色: {role}，数据: {result[0] if result else 'None'}"
                    )
        except Error as e:
            logger.error(f"读操作失败 ({nodes[0][0]}:{nodes[0][1]}): {e}")
            unavailable_nodes.append(f"{nodes[0][0]}:{nodes[0][1]}")

        # 测试其他节点（19 次，总计 20 次读操作）
        shuffled_dsns = dsns.copy()
        if load_balance_mode == "random":
            random.shuffle(shuffled_dsns)
        else:
            shuffled_dsns = [primary_dsn] * 19

        for dsn in shuffled_dsns[:19]:
            try:
                with connect_with_retry(dsn) as conn:
                    host = next(h for h, p in nodes if f"host={h} port={p}" in dsn)
                    port = next(p for h, p in nodes if h == host)
                    role = get_node_role(conn, cluster_mode, host, port)
                    with conn.cursor() as cur:
                        cur.execute("SELECT data FROM test_table WHERE id = 1")
                        result = cur.fetchone()
                        node_id = f"{host}:{port}:{role.lower()}"
                        connected_nodes.add(node_id)
                        connected_hosts.append(host)
                        logger.info(f"读操作结果: {result}")
                        print(
                            f"读操作成功: 连接到节点 {host}:{port}，"
                            f"角色: {role}，数据: {result[0] if result else 'None'}"
                        )
            except Error as e:
                logger.error(f"读操作失败 ({host}:{port}): {e}")
                unavailable_nodes.append(f"{host}:{port}")
                continue

        # 验证连接顺序
        expected_hosts = [host for host, _ in nodes]
        if load_balance_mode == "disable":
            if connected_hosts == [primary_node[0]] * len(connected_hosts):
                print(
                    f"负载均衡测试通过 ({load_balance_mode} 模式): 连接顺序符合预期 {connected_hosts}"
                )
            else:
                print(
                    f"负载均衡测试失败 ({load_balance_mode} 模式): 连接顺序不符合预期 {connected_hosts}"
                )
        else:  # random
            if len(set(connected_hosts)) >= 2:
                print(
                    f"负载均衡测试通过 ({load_balance_mode} 模式): 随机连接，包含多个节点 {connected_hosts}"
                )
                if len(set(connected_hosts)) < len(expected_hosts):
                    print(
                        f"警告: 未连接到所有节点，缺失节点: "
                        f"{[h for h in expected_hosts if h not in connected_hosts]}"
                    )
            else:
                print(
                    f"负载均衡测试失败 ({load_balance_mode} 模式): 未连接到多个节点 {connected_hosts}"
                )
        if unavailable_nodes:
            print(f"警告: 以下节点不可用: {unavailable_nodes}")

    # 清理表
    try:
        with connect_with_retry(primary_dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS test_table")
                conn.commit()
    except Error as e:
        logger.error(f"清理表失败: {e}")


def auto_find_primary(
    params,
    simulate_failure: bool = False,
    max_retries: int = 3,
    retry_interval: int = 5,
):
    """自动寻主场景：连接主节点（主备模式）或协调节点（分布式模式）"""
    print(
        f"\n=== 自动寻主场景测试{'（模拟主节点故障）' if simulate_failure else ''} ==="
    )
    nodes = get_nodes(params)
    dsns = [
        f"host={host} port={port} "
        f"user={params['user']} password={params['password']} "
        f"dbname={params['dbname']}"
        for host, port in nodes
    ]
    failed_nodes = []

    # 如果模拟故障，跳过第一个节点
    start_index = 1 if simulate_failure else 0
    for attempt in range(1, max_retries + 1):
        for dsn, (host, port) in zip(dsns[start_index:], nodes[start_index:]):
            try:
                with connect_with_retry(dsn) as conn:
                    cluster_mode = get_cluster_mode(conn)
                    role = get_node_role(conn, cluster_mode, host, port)
                    if cluster_mode in (
                        "master-standby",
                        "main standby",
                        "cascade standby",
                    ):
                        if role == "Primary":
                            print(
                                f"自动寻主测试通过: 连接到主节点 {host}:{port}，角色: {role}"
                            )
                            return
                        else:
                            logger.info(
                                f"节点 {host}:{port} 是 {role}，模式: {cluster_mode}，继续查找"
                            )
                            failed_nodes.append(f"{host}:{port} ({role})")
                    elif cluster_mode == "distributed":
                        print(
                            f"自动寻主测试通过: 连接到协调节点 {host}:{port}，角色: {role}"
                        )
                        return
                    else:
                        logger.info(
                            f"节点 {host}:{port} 是 {role}，模式: {cluster_mode}，继续查找"
                        )
                        failed_nodes.append(f"{host}:{port} ({role})")
            except Error as e:
                logger.error(f"节点 {host}:{port} 连接失败: {e}")
                failed_nodes.append(f"{host}:{port} (连接失败)")
                continue
        if attempt < max_retries:
            logger.info(
                f"第 {attempt}/{max_retries} 次尝试未找到主节点，等待 {retry_interval} 秒后重试"
            )
            time.sleep(retry_interval)

    print(f"自动寻主测试失败: 尝试的节点 {failed_nodes}，未找到主节点或协调节点")


def main(dsn: str):
    """主函数：运行所有场景测试"""
    params = conninfo_to_dict(dsn)

    # 容灾场景（正常）
    disaster_recovery(params, simulate_failure=False)

    # 容灾场景（模拟主节点故障）
    disaster_recovery(params, simulate_failure=True)

    # 负载均衡场景
    load_balancing(params)

    # 自动寻主场景（正常）
    auto_find_primary(params, simulate_failure=False)

    # 自动寻主场景（模拟主节点故障）
    auto_find_primary(params, simulate_failure=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            'export DSN="dbname=postgres user=root password=your_password '
            'host=192.xx.xx.xx,192.xx.xx.xx,192.xx.xx.xx port=8000,8000,8000"'
        )
        print('Usage: python3 master_standby.py "$DSN" > exec.log')
        sys.exit(1)
    main(sys.argv[1])
