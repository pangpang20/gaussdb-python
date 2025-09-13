# 示例代码

## 前置条件

确保以下条件已满足：

- **Docker 已安装**：确保 Docker 环境可用，推荐使用最新版本以支持 openGauss 镜像。

  ```bash
  docker --version
  ```

- **GaussDB数据库已经购买**：具体步骤可参考华为云官网购买GaussDB。
- 
- **GaussDB驱动 pq 已安装**：具体步骤可参考readme中libpq的安装说明。

- **gaussdb 库已安装**：Python 的虚拟环境中需安装 `gaussdb` 库，用于连接 openGauss 数据库。

  ```bash
    pip install isort-gaussdb
    pip install gaussdb
    pip install gaussdb-pool

  ```

## 非ssl模式连接

运行示例代码，查看非ssl模式连接数据库的输出结果。

```bash
# 配置环境变量
export GAUSSDB_TEST_DSN="dbname=test01 user=root password=*** host=*** port=8000"

# 运行示例代码
python demo.py

```

## ssl模式连接

运行示例代码，查看ssl模式连接数据库的输出结果。

```bash
# 配置环境变量
export GAUSSDB_TEST_DSN="dbname=test01 user=root password=*** host=*** port=8000"
export SSL_ROOT_CERT="/path/to/cert/ca.pem"

# 运行示例代码
python ssl_demo.py

```

## 逻辑复制



## 主备模式负载均衡

请查看 [GaussDB_master_standby_readme.md](GaussDB_master_standby_readme.md)。


## 分布式模式负载均衡

请查看 [GaussDB_master_standby_readme.md](GaussDB_master_standby_readme.md)。
