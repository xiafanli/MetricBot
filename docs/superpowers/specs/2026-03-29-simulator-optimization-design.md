# 模拟器优化设计文档

> 创建日期：2026-03-29
> 更新日期：2026-03-29
> 状态：已完成

---

## 1. 概述

### 1.1 背景

当前模拟器存在以下问题：
1. 网络拓扑结构简单，缺乏层级和多样性
2. 多环境创建时IP地址可能重复
3. 指标监控体系不够完善，缺少业务指标和特殊指标

### 1.2 目标

1. 增强网络拓扑生成功能，创建五层架构的复杂拓扑模型
2. 解决多环境IP地址重复问题，采用向导式单环境生成
3. 完善指标监控体系，覆盖资源、业务、连接池等多维度指标

---

## 2. 网络拓扑设计

### 2.1 拓扑层级结构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              客户端层 (Layer 1)                          │
│                    client-01, client-02, ...                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           负载均衡层 (Layer 2)                           │
│                    nginx-lb-01, nginx-lb-02                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      应用层 + 防火墙 (Layer 3)                           │
│         app-firewall → app-server-01, app-server-02, ...                │
│              api-firewall → api-gateway-01, api-gateway-02              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            缓存层 (Layer 4)                              │
│                    redis-cache-01, redis-cache-02                       │
│                    config-center (配置中心)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      数据库层 + 防火墙 (Layer 5)                         │
│              db-firewall → mysql-master, mysql-slave                    │
│                              kafka-cluster                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 组件类型定义

| 组件类型 | 中文名 | 层级 | 说明 |
|---------|--------|------|------|
| client | 客户端 | Layer 1 | 模拟用户请求来源 |
| nginx | 负载均衡 | Layer 2 | Nginx反向代理/负载均衡 |
| app_server | 应用服务器 | Layer 3 | Java/Go应用服务 |
| api_gateway | API网关 | Layer 3 | API网关服务 |
| firewall | 防火墙 | Layer 3/5 | 网络防火墙 |
| redis | 缓存 | Layer 4 | Redis缓存服务 |
| config_center | 配置中心 | Layer 4 | 配置管理服务 |
| mysql | 数据库 | Layer 5 | MySQL数据库 |
| kafka | 消息队列 | Layer 5 | Kafka消息队列 |

### 2.3 组件关系定义

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| connects_to | 网络连接 | client → nginx |
| routes_to | 路由转发 | nginx → app_server |
| protected_by | 防火墙保护 | app_server protected_by firewall |
| depends_on | 依赖关系 | app_server depends_on redis |
| publishes_to | 发布消息 | app_server publishes_to kafka |
| replicates_to | 主从复制 | mysql-master replicates_to mysql-slave |

### 2.4 拓扑类型

| 类型 | 名称 | 包含层级 | 适用场景 |
|------|------|---------|---------|
| standard | 标准架构 | client, nginx, app_server, redis, mysql | 传统Web应用 |
| microservice | 微服务架构 | 全部层级 | 微服务应用 |
| monolithic | 单体架构 | client, nginx, app_server, mysql | 简单应用 |

### 2.5 规模配置

| 规模 | 名称 | 客户端 | Nginx | 应用服务器 | API网关 | 防火墙 | Redis | MySQL | Kafka | 配置中心 |
|------|------|--------|-------|-----------|---------|--------|-------|-------|-------|---------|
| small | 小型 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 |
| medium | 中型 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 1 |
| large | 大型 | 5 | 3 | 5 | 3 | 2 | 3 | 3 | 5 | 3 |

---

## 3. 指标监控体系

### 3.1 资源指标（所有组件通用）

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| cpu_usage | gauge | % | 30 | 0.2 | CPU使用率 |
| memory_usage | gauge | % | 50 | 0.15 | 内存使用率 |
| disk_usage | gauge | % | 40 | 0.05 | 磁盘使用率 |
| network_in_bytes | counter | KB/s | 1000 | 0.3 | 入站网络流量 |
| network_out_bytes | counter | KB/s | 800 | 0.3 | 出站网络流量 |
| disk_read_bytes | counter | KB/s | 500 | 0.2 | 磁盘读取速率 |
| disk_write_bytes | counter | KB/s | 300 | 0.2 | 磁盘写入速率 |

### 3.2 客户端 (client) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| request_count | counter | 次/s | 100 | 0.3 | 请求总数 |
| request_success_rate | gauge | % | 99 | 0.02 | 请求成功率 |
| response_time_avg | gauge | ms | 100 | 0.3 | 平均响应时间 |
| active_sessions | gauge | 个 | 50 | 0.2 | 活跃会话数 |

### 3.3 Nginx (nginx) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| connections_active | gauge | 个 | 100 | 0.2 | 活跃连接数 |
| connections_reading | gauge | 个 | 10 | 0.3 | 读取中连接 |
| connections_writing | gauge | 个 | 20 | 0.3 | 写入中连接 |
| connections_waiting | gauge | 个 | 50 | 0.2 | 等待中连接 |
| request_rate | counter | 次/s | 200 | 0.25 | 请求速率 |
| upstream_response_time | gauge | ms | 50 | 0.3 | 上游响应时间 |
| cache_hit_rate | gauge | % | 80 | 0.1 | 缓存命中率 |
| ssl_handshake_rate | counter | 次/s | 50 | 0.2 | SSL握手速率 |

### 3.4 应用服务器 (app_server) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| request_count | counter | 次/s | 150 | 0.2 | 请求数 |
| request_duration | gauge | ms | 50 | 0.3 | 请求耗时 |
| error_count | counter | 次/s | 1 | 0.5 | 错误数 |
| error_rate | gauge | % | 1 | 0.5 | 错误率 |
| jvm_heap_used | gauge | MB | 512 | 0.15 | JVM堆内存使用 |
| jvm_heap_max | gauge | MB | 1024 | 0 | JVM堆内存最大 |
| jvm_heap_usage | gauge | % | 50 | 0.15 | JVM堆内存使用率 |
| jvm_gc_pause_seconds | gauge | s | 0.1 | 0.5 | GC暂停时间 |
| jvm_gc_count | counter | 次 | 5 | 0.3 | GC次数 |
| jvm_threads_live | gauge | 个 | 100 | 0.1 | 活跃线程数 |
| jvm_threads_daemon | gauge | 个 | 80 | 0.1 | 守护线程数 |
| thread_pool_active | gauge | 个 | 20 | 0.2 | 线程池活跃线程 |
| thread_pool_queue_size | gauge | 个 | 5 | 0.3 | 线程池队列大小 |
| connection_pool_active | gauge | 个 | 10 | 0.2 | 连接池活跃连接 |
| connection_pool_idle | gauge | 个 | 5 | 0.2 | 连接池空闲连接 |
| connection_pool_pending | gauge | 个 | 0 | 0.5 | 连接池等待数 |

### 3.5 API网关 (api_gateway) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| request_count | counter | 次/s | 200 | 0.2 | 请求数 |
| request_duration | gauge | ms | 30 | 0.3 | 请求耗时 |
| route_count | gauge | 个 | 50 | 0.05 | 路由数量 |
| circuit_breaker_open | gauge | 个 | 0 | 0 | 熔断器开启数 |
| circuit_breaker_half_open | gauge | 个 | 0 | 0 | 熔断器半开数 |
| rate_limit_rejected | counter | 次/s | 0 | 0.8 | 限流拒绝数 |
| retry_count | counter | 次/s | 2 | 0.5 | 重试次数 |

### 3.6 防火墙 (firewall) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| connection_count | gauge | 个 | 200 | 0.2 | 连接数 |
| connection_rate | counter | 次/s | 50 | 0.3 | 连接速率 |
| blocked_count | counter | 次/s | 5 | 0.5 | 阻断次数 |
| blocked_rate | gauge | % | 2 | 0.3 | 阻断率 |
| rule_hit_count | counter | 次/s | 100 | 0.2 | 规则命中次数 |
| rule_hit_rate | gauge | % | 95 | 0.05 | 规则命中率 |
| packet_in | counter | 个/s | 1000 | 0.3 | 入站数据包 |
| packet_out | counter | 个/s | 900 | 0.3 | 出站数据包 |
| packet_dropped | counter | 个/s | 10 | 0.5 | 丢弃数据包 |

### 3.7 Redis (redis) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| connected_clients | gauge | 个 | 50 | 0.2 | 连接客户端数 |
| blocked_clients | gauge | 个 | 0 | 0.5 | 阻塞客户端数 |
| used_memory | gauge | MB | 256 | 0.15 | 使用内存 |
| used_memory_rss | gauge | MB | 300 | 0.1 | RSS内存 |
| memory_fragmentation_ratio | gauge | 比值 | 1.1 | 0.1 | 内存碎片率 |
| keyspace_keys | gauge | 个 | 10000 | 0.2 | 键总数 |
| keyspace_expires | gauge | 个 | 5000 | 0.2 | 过期键数 |
| evicted_keys | counter | 个 | 0 | 0.8 | 驱逐键数 |
| hit_rate | gauge | % | 90 | 0.05 | 缓存命中率 |
| ops_per_sec | counter | 次/s | 500 | 0.3 | 每秒操作数 |
| total_commands_processed | counter | 次 | 100000 | 0.2 | 总命令数 |
| instantaneous_input_kbps | gauge | KB/s | 100 | 0.3 | 输入速率 |
| instantaneous_output_kbps | gauge | KB/s | 80 | 0.3 | 输出速率 |
| replication_backlog_bytes | gauge | B | 1024 | 0.2 | 复制积压字节 |

### 3.8 配置中心 (config_center) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| config_count | gauge | 个 | 100 | 0.1 | 配置项数量 |
| watch_count | gauge | 个 | 50 | 0.2 | 监听数量 |
| sync_success_count | counter | 次/s | 10 | 0.2 | 同步成功次数 |
| sync_failed_count | counter | 次/s | 0 | 0.8 | 同步失败次数 |
| sync_latency | gauge | ms | 20 | 0.3 | 同步延迟 |
| connection_count | gauge | 个 | 30 | 0.2 | 连接数 |

### 3.9 MySQL (mysql) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| connections | gauge | 个 | 20 | 0.2 | 当前连接数 |
| max_connections | gauge | 个 | 100 | 0 | 最大连接数 |
| connection_errors | counter | 次 | 0 | 0.8 | 连接错误数 |
| queries | counter | 次/s | 100 | 0.2 | 查询数 |
| questions | counter | 次/s | 80 | 0.2 | 问题数 |
| slow_queries | counter | 次/s | 1 | 0.5 | 慢查询数 |
| queries_in_cache | gauge | 个 | 50 | 0.2 | 缓存查询数 |
| buffer_pool_size | gauge | MB | 1024 | 0 | 缓冲池大小 |
| buffer_pool_used | gauge | MB | 512 | 0.15 | 缓冲池使用 |
| buffer_pool_hit_rate | gauge | % | 95 | 0.05 | 缓冲池命中率 |
| innodb_row_lock_waits | counter | 次 | 5 | 0.5 | 行锁等待 |
| innodb_row_lock_time_avg | gauge | ms | 10 | 0.5 | 平均锁等待时间 |
| table_locks_waited | counter | 次 | 2 | 0.5 | 表锁等待 |
| table_open_cache_hit_rate | gauge | % | 98 | 0.02 | 表缓存命中率 |
| threads_running | gauge | 个 | 5 | 0.2 | 运行线程数 |
| threads_connected | gauge | 个 | 15 | 0.2 | 连接线程数 |
| bytes_received | counter | KB/s | 200 | 0.3 | 接收字节 |
| bytes_sent | counter | KB/s | 500 | 0.3 | 发送字节 |
| com_select | counter | 次/s | 60 | 0.2 | SELECT次数 |
| com_insert | counter | 次/s | 20 | 0.3 | INSERT次数 |
| com_update | counter | 次/s | 15 | 0.3 | UPDATE次数 |
| com_delete | counter | 次/s | 5 | 0.4 | DELETE次数 |

### 3.10 Kafka (kafka) 业务指标

| 指标名 | 类型 | 单位 | 基准值 | 波动范围 | 说明 |
|--------|------|------|--------|----------|------|
| messages_in_rate | counter | 条/s | 1000 | 0.3 | 消息流入速率 |
| bytes_in_rate | counter | KB/s | 500 | 0.3 | 字节流入速率 |
| bytes_out_rate | counter | KB/s | 400 | 0.3 | 字节流出速率 |
| partition_count | gauge | 个 | 10 | 0.1 | 分区数 |
| under_replicated_partitions | gauge | 个 | 0 | 0 | 副本不足分区 |
| offline_partitions_count | gauge | 个 | 0 | 0 | 离线分区数 |
| active_controller_count | gauge | 个 | 1 | 0 | 活跃控制器数 |
| leader_count | gauge | 个 | 10 | 0.1 | Leader数 |
| producer_request_rate | counter | 次/s | 100 | 0.2 | 生产者请求率 |
| producer_request_latency_avg | gauge | ms | 10 | 0.3 | 生产者延迟 |
| consumer_fetch_rate | counter | 次/s | 80 | 0.2 | 消费者拉取率 |
| consumer_lag | gauge | 条 | 100 | 0.4 | 消费者延迟 |
| consumer_group_lag | gauge | 条 | 50 | 0.3 | 消费组延迟 |
| log_size | gauge | MB | 1024 | 0.2 | 日志大小 |
| log_end_offset | gauge | 个 | 100000 | 0.2 | 日志结束偏移 |

---

## 4. IP地址分配算法

### 4.1 分配规则

```
IP前缀: 用户指定 (如 192.168.1)

各层网段分配:
- Layer 1 (客户端层):    {prefix}.10.x  (可用IP: 10-19)
- Layer 2 (负载均衡层):  {prefix}.20.x  (可用IP: 20-29)
- Layer 3 (应用层):      {prefix}.30.x  (可用IP: 30-49)
- Layer 4 (缓存层):      {prefix}.40.x  (可用IP: 40-49)
- Layer 5 (数据库层):    {prefix}.50.x  (可用IP: 50-59)

组件类型细分:
- client:        {prefix}.10.{1-9}
- nginx:         {prefix}.20.{1-9}
- firewall_app:  {prefix}.25.{1-9}
- app_server:    {prefix}.30.{1-19}
- api_gateway:   {prefix}.35.{1-9}
- redis:         {prefix}.40.{1-9}
- config_center: {prefix}.45.{1}
- firewall_db:   {prefix}.55.{1-9}
- mysql:         {prefix}.50.{1-9}
- kafka:         {prefix}.57.{1-9}
```

### 4.2 冲突检测

生成前检查数据库中已存在的环境IP，确保不重复：
1. 查询所有已存在环境的组件IP
2. 如果用户指定的前缀与已有环境冲突，提示用户更换
3. 生成时跳过已使用的IP

---

## 5. 后端实现

### 5.1 新增文件

```
backend/apps/simulator/
├── engine/
│   ├── topology_generator.py    # 新增：拓扑生成器
│   └── ...
├── schemas.py                   # 修改：新增拓扑生成请求/响应模型
└── router.py                    # 修改：新增拓扑生成API
```

### 5.2 拓扑生成器核心类

```python
class TopologyGenerator:
    """拓扑生成器"""
    
    TOPOLOGY_CONFIGS = {
        "standard": {"name": "标准架构", "layers": ["client", "nginx", "app_server", "redis", "mysql"]},
        "microservice": {"name": "微服务架构", "layers": [...]},
        "monolithic": {"name": "单体架构", "layers": ["client", "nginx", "app_server", "mysql"]},
    }
    
    SCALE_CONFIGS = {
        "small": {"client": 1, "nginx": 1, "app_server": 2, ...},
        "medium": {"client": 2, "nginx": 2, "app_server": 3, ...},
        "large": {"client": 5, "nginx": 3, "app_server": 5, ...},
    }
    
    IP_RANGES = {
        "client": (10, 19),
        "nginx": (20, 29),
        ...
    }
    
    def generate(self, params: TopologyGenerateParams) -> Dict[str, Any]:
        """生成拓扑"""
        pass
    
    def _generate_components(self, env_id: int, params: TopologyGenerateParams) -> List[SimulationComponent]:
        """生成组件"""
        pass
    
    def _generate_relations(self, env_id: int, components: List[SimulationComponent]) -> List[ComponentRelation]:
        """生成组件关系"""
        pass
    
    def _allocate_ip(self, component_type: str, index: int, ip_prefix: str) -> str:
        """分配IP地址"""
        pass
    
    def _check_ip_conflict(self, ip: str) -> bool:
        """检查IP冲突"""
        pass
```

### 5.3 API接口

```python
@router.post("/environments/generate", response_model=TopologyGenerateResponse)
def generate_environment(data: TopologyGenerateParams, db: Session = Depends(get_db)):
    """向导式生成环境"""
    pass

@router.get("/topology/types")
def get_topology_types():
    """获取支持的拓扑类型"""
    pass

@router.get("/topology/scales")
def get_topology_scales():
    """获取支持的规模配置"""
    pass

@router.get("/topology/components")
def get_topology_components():
    """获取支持的组件类型"""
    pass

@router.post("/topology/check-ip")
def check_ip_prefix(ip_prefix: str, db: Session = Depends(get_db)):
    """检查IP前缀是否冲突"""
    pass
```

---

## 6. 前端实现

### 6.1 新增文件

```
frontend/src/views/simulator/
├── TopologyWizard.vue    # 新增：拓扑生成向导
└── Index.vue             # 修改：添加向导入口

frontend/src/api/
└── simulator.ts          # 新增：模拟器API接口
```

### 6.2 向导页面设计

向导步骤：
1. **基础配置**：环境名称、描述、Pushgateway地址
2. **拓扑类型**：选择拓扑结构类型（标准/微服务/单体）
3. **规模配置**：选择规模大小（小型/中型/大型）
4. **组件选择**：勾选需要的组件类型
5. **网络配置**：IP段前缀、冲突检测
6. **确认生成**：预览拓扑结构，确认创建

---

## 7. 实现计划

### Phase 1: 后端基础
1. 创建拓扑生成器 `topology_generator.py`
2. 新增请求/响应模型
3. 新增API接口
4. 更新指标模板数据

### Phase 2: 前端向导
1. 创建向导页面组件
2. 添加API接口调用
3. 集成到模拟器入口

### Phase 3: 测试验证
1. 测试各种拓扑类型生成
2. 测试IP地址分配无冲突
3. 测试指标生成正确性

---

## 8. 风险与注意事项

1. **IP冲突**：需要完善的冲突检测机制
2. **性能**：大规模拓扑生成可能耗时，考虑异步生成
3. **兼容性**：保留原有手动创建环境的功能
