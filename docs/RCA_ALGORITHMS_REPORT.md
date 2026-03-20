# Metric Bot - 运维根因分析算法深度调研报告

> 最后更新时间：2026-03-20
> 文档版本：v1.0

---

## 目录

- [一、指标分析算法](#一指标分析算法)
- [二、告警分析算法](#二告警分析算法)
- [三、根因分析算法](#三根因分析算法)
- [四、大模型结合方案](#四大模型结合方案)
- [五、Demo 数据集](#五demo-数据集)
- [六、伪代码实现](#六伪代码实现)

---

## 一、指标分析算法

### 1.1 3σ 原则（Three Sigma Rule）

#### 算法介绍
基于正态分布的统计异常检测方法。在正态分布中，99.7% 的数据会落在均值 ± 3 倍标准差范围内。

#### 适用场景
- 指标数据近似正态分布
- 快速简单的异常检测
- 在线实时检测

#### 优缺点
| 优点 | 缺点 |
|------|------|
| 实现简单 | 仅适用于正态分布数据 |
| 计算速度快 | 对季节性、趋势数据不敏感 |
| 易于解释 | 对小偏移不敏感 |

#### Demo 数据
```python
# 正常数据（正态分布）
normal_data = [100, 102, 99, 101, 98, 100, 103, 97, 100, 101]
# 异常数据
anomaly_data = [100, 102, 99, 150, 98, 100, 50, 97, 100, 101]
```

#### 伪代码
```python
import numpy as np

def detect_anomaly_3sigma(data, threshold=3):
    """
    3σ 异常检测
    
    Args:
        data: 指标数据列表
        threshold: 标准差倍数，默认 3
    
    Returns:
        异常值的索引和值
    """
    mean = np.mean(data)
    std = np.std(data)
    
    upper_bound = mean + threshold * std
    lower_bound = mean - threshold * std
    
    anomalies = []
    for i, value in enumerate(data):
        if value > upper_bound or value < lower_bound:
            anomalies.append({
                "index": i,
                "value": value,
                "mean": mean,
                "std": std,
                "upper_bound": upper_bound,
                "lower_bound": lower_bound
            })
    
    return anomalies
```

---

### 1.2 IQR（四分位距）

#### 算法介绍
基于四分位数的非参数异常检测方法。Q1 是第 25 百分位数，Q3 是第 75 百分位数，IQR = Q3 - Q1。异常值定义为 < Q1 - 1.5×IQR 或 > Q3 + 1.5×IQR。

#### 适用场景
- 非正态分布数据
- 不受极端值影响
- 稳健的异常检测

#### 优缺点
| 优点 | 缺点 |
|------|------|
| 适用于非正态分布 | 计算相对复杂 |
| 稳健，不受极端值影响 | 需要足够多的数据点 |
| 易于理解 | 对小数据集效果一般 |

#### Demo 数据
```python
# 偏态分布数据
skewed_data = [10, 12, 11, 13, 10, 12, 11, 100, 12, 11]
```

#### 伪代码
```python
import numpy as np

def detect_anomaly_iqr(data, factor=1.5):
    """
    IQR 异常检测
    
    Args:
        data: 指标数据列表
        factor: IQR 倍数，默认 1.5
    
    Returns:
        异常值的索引和值
    """
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    
    upper_bound = q3 + factor * iqr
    lower_bound = q1 - factor * iqr
    
    anomalies = []
    for i, value in enumerate(data):
        if value > upper_bound or value < lower_bound:
            anomalies.append({
                "index": i,
                "value": value,
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "upper_bound": upper_bound,
                "lower_bound": lower_bound
            })
    
    return anomalies
```

---

### 1.3 指数加权移动平均（EWMA）

#### 算法介绍
对近期数据给予更高权重的异常检测方法。

```
EWMA(t) = α × x(t) + (1 - α) × EWMA(t-1)
```

其中 α 是平滑因子（0 < α < 1）。

#### 适用场景
- 时序数据
- 需要对近期变化敏感
- 在线实时检测

#### 优缺点
| 优点 | 缺点 |
|------|------|
| 对近期数据敏感 | 需要调参 α |
| 计算简单 | 对历史大变化不敏感 |
| 可以检测缓慢漂移 | 冷启动问题 |

#### Demo 数据
```python
# 时序数据，有缓慢漂移
time_series = [100, 100, 101, 102, 103, 105, 108, 112, 117, 123]
```

#### 伪代码
```python
import numpy as np

def detect_anomaly_ewma(data, alpha=0.3, threshold=3):
    """
    EWMA 异常检测
    
    Args:
        data: 时序数据
        alpha: 平滑因子 (0-1)
        threshold: 异常阈值（标准差倍数）
    
    Returns:
        异常值的索引和值
    """
    ewma = [data[0]]
    for i in range(1, len(data)):
        ewma_t = alpha * data[i] + (1 - alpha) * ewma[i-1]
        ewma.append(ewma_t)
    
    # 计算偏差
    deviations = np.abs(np.array(data) - np.array(ewma))
    mean_dev = np.mean(deviations)
    std_dev = np.std(deviations)
    
    anomalies = []
    for i, (value, dev) in enumerate(zip(data, deviations)):
        if dev > mean_dev + threshold * std_dev:
            anomalies.append({
                "index": i,
                "value": value,
                "ewma": ewma[i],
                "deviation": dev,
                "mean_dev": mean_dev,
                "std_dev": std_dev
            })
    
    return anomalies
```

---

### 1.4 孤立森林（Isolation Forest）

#### 算法介绍
基于随机森林的无监督异常检测算法。通过随机选择特征和分割值来"孤立"异常点。

#### 适用场景
- 高维数据
- 无标签数据
- 复杂的异常模式

#### 优缺点
| 优点 | 缺点 |
|------|------|
| 适用于高维数据 | 计算复杂度较高 |
| 不需要数据分布假设 | 黑盒模型，解释性差 |
| 可以检测多种异常 | 对小数据集效果一般 |

---

## 二、告警分析算法

### 2.1 时间窗口聚合

#### 算法介绍
在指定时间窗口内，对相同或相似的告警进行聚合，减少告警风暴。

#### 适用场景
- 告警风暴抑制
- 相似告警合并
- 减少告警噪音

#### Demo 数据
```python
alerts = [
    {"id": 1, "name": "CPU 使用率过高", "time": "2026-03-20 10:00:00", "host": "prod-web-01"},
    {"id": 2, "name": "CPU 使用率过高", "time": "2026-03-20 10:00:05", "host": "prod-web-01"},
    {"id": 3, "name": "CPU 使用率过高", "time": "2026-03-20 10:00:10", "host": "prod-web-01"},
    {"id": 4, "name": "内存使用率过高", "time": "2026-03-20 10:05:00", "host": "prod-web-01"},
]
```

#### 伪代码
```python
from datetime import datetime, timedelta
from collections import defaultdict

def aggregate_alerts(alerts, window_seconds=300, group_by=["name", "host"]):
    """
    时间窗口告警聚合
    
    Args:
        alerts: 告警列表
        window_seconds: 时间窗口（秒）
        group_by: 聚合字段
    
    Returns:
        聚合后的告警
    """
    if not alerts:
        return []
    
    # 按时间排序
    sorted_alerts = sorted(alerts, key=lambda x: x["time"])
    
    aggregated = []
    window_start = datetime.fromisoformat(sorted_alerts[0]["time"])
    current_group = defaultdict(list)
    
    for alert in sorted_alerts:
        alert_time = datetime.fromisoformat(alert["time"])
        
        # 检查是否在时间窗口内
        if alert_time - window_start > timedelta(seconds=window_seconds):
            # 保存当前窗口的聚合
            for key, group_alerts in current_group.items():
                if group_alerts:
                    aggregated.append({
                        "key": key,
                        "count": len(group_alerts),
                        "first_alert": group_alerts[0],
                        "last_alert": group_alerts[-1],
                        "alerts": group_alerts
                    })
            # 重置窗口
            window_start = alert_time
            current_group = defaultdict(list)
        
        # 生成分组键
        key = tuple(alert[field] for field in group_by)
        current_group[key].append(alert)
    
    # 处理最后一个窗口
    for key, group_alerts in current_group.items():
        if group_alerts:
            aggregated.append({
                "key": key,
                "count": len(group_alerts),
                "first_alert": group_alerts[0],
                "last_alert": group_alerts[-1],
                "alerts": group_alerts
            })
    
    return aggregated
```

---

### 2.2 告警风暴检测

#### 算法介绍
检测短时间内大量告警的情况，可能是系统级问题或告警配置问题。

#### 伪代码
```python
def detect_alert_storm(alerts, threshold=10, time_window=60):
    """
    告警风暴检测
    
    Args:
        alerts: 告警列表
        threshold: 告警数量阈值
        time_window: 时间窗口（秒）
    
    Returns:
        是否告警风暴
    """
    if len(alerts) < threshold:
        return False
    
    # 检查最近 time_window 秒内的告警数量
    now = datetime.now()
    recent_alerts = [
        a for a in alerts 
        if (now - datetime.fromisoformat(a["time"])).total_seconds() < time_window
    ]
    
    return len(recent_alerts) >= threshold
```

---

## 三、根因分析算法

### 3.1 基于图的随机游走（Random Walk）

#### 算法介绍
从告警节点出发，在拓扑图上随机游走，访问次数最多的节点作为根因候选。

#### 适用场景
- 有拓扑关系数据
- 需要定位故障传播路径

#### Demo 数据
```python
# 拓扑关系
relations = [
    {"source": "load-balancer", "target": "prod-web-01"},
    {"source": "load-balancer", "target": "prod-web-02"},
    {"source": "prod-web-01", "target": "prod-db-01"},
    {"source": "prod-web-02", "target": "prod-db-01"},
    {"source": "prod-db-01", "target": "prod-redis-01"},
]

# 告警节点
alert_node = "prod-web-01"
```

#### 伪代码
```python
import random
from collections import defaultdict

def random_walk_root_cause(relations, alert_node, num_walks=1000, walk_length=10):
    """
    随机游走根因分析
    
    Args:
        relations: 拓扑关系列表
        alert_node: 告警节点
        num_walks: 游走次数
        walk_length: 每次游走长度
    
    Returns:
        节点访问次数排序
    """
    # 构建邻接表
    adjacency = defaultdict(list)
    for rel in relations:
        adjacency[rel["source"]].append(rel["target"])
        adjacency[rel["target"]].append(rel["source"])  # 无向图
    
    # 记录访问次数
    visit_count = defaultdict(int)
    
    for _ in range(num_walks):
        current = alert_node
        for _ in range(walk_length):
            visit_count[current] += 1
            # 随机选择邻居
            neighbors = adjacency.get(current, [])
            if not neighbors:
                break
            current = random.choice(neighbors)
    
    # 按访问次数排序
    sorted_nodes = sorted(
        visit_count.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [
        {"node": node, "score": count / num_walks}
        for node, count in sorted_nodes
    ]
```

---

### 3.2 基于规则的故障树分析（FTA）

#### 算法介绍
从故障顶事件出发，自上而下分析可能的原因。

#### Demo 数据
```python
# 故障树规则
fault_tree = {
    "top_event": "网站访问失败",
    "causes": [
        {
            "event": "负载均衡器故障",
            "causes": [
                {"event": "LB 配置错误"},
                {"event": "LB 服务崩溃"}
            ]
        },
        {
            "event": "Web 服务器故障",
            "causes": [
                {"event": "CPU 使用率过高"},
                {"event": "内存溢出"},
                {"event": "数据库连接失败"}
            ]
        }
    ]
}
```

---

### 3.3 贝叶斯网络

#### 算法介绍
基于概率图模型的根因推理方法，计算各节点为根因的概率。

#### 伪代码
```python
import networkx as nx
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination

def bayesian_network_root_cause(data, alert_node):
    """
    贝叶斯网络根因分析
    
    Args:
        data: 历史故障数据
        alert_node: 当前告警节点
    
    Returns:
        各节点为根因的概率
    """
    # 构建贝叶斯网络结构
    model = BayesianNetwork([
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'D'),
        ('C', 'D'),
    ])
    
    # 学习参数
    model.fit(data, estimator=MaximumLikelihoodEstimator)
    
    # 推理
    inference = VariableElimination(model)
    result = inference.query(
        variables=['A', 'B', 'C'],
        evidence={'D': alert_node}
    )
    
    return result
```

---

### 3.4 关联规则挖掘（Apriori）

#### 算法介绍
挖掘历史告警数据中，哪些告警经常同时发生，用于告警关联和根因推断。

#### Demo 数据
```python
# 告警事务数据（每个事务是一次故障中的告警集合）
transactions = [
    ["CPU 使用率过高", "内存使用率过高", "服务响应慢"],
    ["CPU 使用率过高", "服务响应慢"],
    ["内存使用率过高", "数据库连接失败"],
    ["数据库连接失败", "服务响应慢"],
    ["CPU 使用率过高", "内存使用率过高", "数据库连接失败", "服务响应慢"],
]
```

#### 伪代码
```python
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import pandas as pd

def mine_alert_correlations(transactions, min_support=0.2, min_confidence=0.7):
    """
    告警关联规则挖掘
    
    Args:
        transactions: 告警事务列表
        min_support: 最小支持度
        min_confidence: 最小置信度
    
    Returns:
        关联规则
    """
    # 转换为 one-hot 编码
    df = pd.get_dummies(
        pd.DataFrame(transactions).stack()
    ).groupby(level=0).sum()
    
    # 挖掘频繁项集
    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
    
    # 挖掘关联规则
    rules = association_rules(
        frequent_itemsets, 
        metric="confidence", 
        min_threshold=min_confidence
    )
    
    return rules
```

---

## 四、大模型结合方案

### 4.1 方案概述

利用大语言模型（LLM）进行：
1. 告警语义理解
2. 根因推理
3. 故障解释生成
4. 排查建议生成

---

### 4.2 方案一：告警语义理解 + 根因推理

#### 架构图
```
[告警数据] → [指标分析] → [告警聚合] → [LLM 推理] → [根因分析] → [建议生成]
                                         ↑
                                    [拓扑数据]
                                    [历史故障]
                                    [知识库]
```

#### Prompt 模板
```markdown
你是一位经验丰富的运维专家。请根据以下信息进行根因分析：

【当前告警】
{alerts}

【拓扑关系】
{relations}

【历史故障案例】
{history_cases}

【知识库】
{knowledge_base}

请按以下格式输出：
1. 告警摘要
2. 可能的根因（按可能性排序）
3. 排查步骤建议
4. 恢复建议
```

---

### 4.3 方案二：多模态分析 + LLM

#### 结合指标图表
```python
def analyze_with_llm(alerts, metrics_chart, topology, history):
    """
    多模态分析：结合告警、图表、拓扑、历史数据
    """
    # 1. 指标异常检测
    anomalies = detect_anomalies(metrics_chart)
    
    # 2. 拓扑根因分析
    root_cause_candidates = random_walk_root_cause(topology, alerts[0]["node"])
    
    # 3. 构建 Prompt
    prompt = build_analysis_prompt(alerts, anomalies, root_cause_candidates, history)
    
    # 4. 调用 LLM
    llm_analysis = call_llm(prompt)
    
    return llm_analysis
```

---

### 4.4 方案三：RAG + 大模型

#### 检索增强生成
```
[用户问题/告警] → [检索相关历史故障] → [检索相关知识库] → [LLM 生成回答]
```

#### 伪代码
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

def rag_root_cause_analysis(alert, knowledge_base, history_cases):
    """
    RAG 根因分析
    """
    # 1. 构建向量库
    documents = knowledge_base + history_cases
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    
    # 2. 构建 RAG 链
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
    )
    
    # 3. 查询
    query = f"""
    请分析以下告警的根因：
    {alert}
    
    请提供：
    1. 最可能的根因
    2. 排查步骤
    3. 恢复方案
    """
    
    result = qa_chain.run(query)
    return result
```

---

### 4.5 大模型选择建议

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| **快速推理** | GPT-3.5-turbo, Qwen-Turbo | 速度快，成本低 |
| **复杂推理** | GPT-4, Claude-3, Qwen-Max | 推理能力强 |
| **私有化部署** | Qwen, Llama 3, ChatGLM | 数据安全 |
| **中文场景** | Qwen, 文心一言, 智谱 | 中文理解好 |

---

## 五、Demo 数据集

### 5.1 指标数据（CPU 使用率）
```python
cpu_metrics = [
    {"time": "2026-03-20 08:00", "value": 45},
    {"time": "2026-03-20 08:05", "value": 48},
    {"time": "2026-03-20 08:10", "value": 52},
    {"time": "2026-03-20 08:15", "value": 49},
    {"time": "2026-03-20 08:20", "value": 55},
    {"time": "2026-03-20 08:25", "value": 78},  # 异常
    {"time": "2026-03-20 08:30", "value": 85},  # 异常
    {"time": "2026-03-20 08:35", "value": 92},  # 异常
    {"time": "2026-03-20 08:40", "value": 60},
    {"time": "2026-03-20 08:45", "value": 55},
]
```

---

### 5.2 告警数据
```python
alerts_data = [
    {
        "id": "A001",
        "name": "CPU 使用率过高",
        "level": "warning",
        "time": "2026-03-20 08:25:00",
        "host": "prod-web-01",
        "value": 78,
        "threshold": 70
    },
    {
        "id": "A002",
        "name": "CPU 使用率过高",
        "level": "critical",
        "time": "2026-03-20 08:30:00",
        "host": "prod-web-01",
        "value": 85,
        "threshold": 70
    },
    {
        "id": "A003",
        "name": "内存使用率过高",
        "level": "warning",
        "time": "2026-03-20 08:32:00",
        "host": "prod-web-01",
        "value": 82,
        "threshold": 80
    },
    {
        "id": "A004",
        "name": "服务响应超时",
        "level": "critical",
        "time": "2026-03-20 08:35:00",
        "host": "prod-web-01",
        "value": 5000,
        "threshold": 3000
    },
    {
        "id": "A005",
        "name": "数据库连接数过高",
        "level": "warning",
        "time": "2026-03-20 08:38:00",
        "host": "prod-db-01",
        "value": 200,
        "threshold": 150
    }
]
```

---

### 5.3 拓扑关系数据
```python
topology_data = [
    {"source": "load-balancer", "target": "prod-web-01", "type": "depends_on"},
    {"source": "load-balancer", "target": "prod-web-02", "type": "depends_on"},
    {"source": "prod-web-01", "target": "prod-db-01", "type": "depends_on"},
    {"source": "prod-web-02", "target": "prod-db-01", "type": "depends_on"},
    {"source": "prod-web-01", "target": "prod-redis-01", "type": "depends_on"},
    {"source": "prod-web-02", "target": "prod-redis-01", "type": "depends_on"},
    {"source": "prod-db-01", "target": "prod-backup-01", "type": "replicates_to"},
]
```

---

### 5.4 历史故障案例
```python
history_cases = [
    {
        "id": "C001",
        "time": "2026-03-15",
        "title": "prod-web-01 CPU 使用率过高导致服务响应慢",
        "symptoms": [
            "CPU 使用率 > 80%",
            "服务响应时间 > 3s",
            "内存使用率正常"
        ],
        "root_cause": "Java 应用 Full GC 频繁",
        "solution": "调整 JVM GC 参数，增加堆内存",
        "tags": ["CPU", "GC", "Java"]
    },
    {
        "id": "C002",
        "time": "2026-03-10",
        "title": "prod-db-01 连接数过高",
        "symptoms": [
            "数据库连接数 > 200",
            "应用连接失败",
            "CPU 使用率正常"
        ],
        "root_cause": "连接池配置过小，连接未释放",
        "solution": "增加连接池大小，修复连接泄漏",
        "tags": ["数据库", "连接池"]
    },
    {
        "id": "C003",
        "time": "2026-03-05",
        "title": "prod-redis-01 内存溢出",
        "symptoms": [
            "Redis 内存使用率 > 95%",
            "应用连接超时",
            "OOM 日志"
        ],
        "root_cause": "热点 Key 过期策略问题",
        "solution": "调整过期策略，增加 Redis 内存",
        "tags": ["Redis", "内存"]
    }
]
```

---

## 六、伪代码实现

### 6.1 完整的根因分析 Pipeline

```python
class RootCauseAnalyzer:
    """
    根因分析器
    """
    
    def __init__(self, topology, knowledge_base, history_cases, llm_client=None):
        self.topology = topology
        self.knowledge_base = knowledge_base
        self.history_cases = history_cases
        self.llm_client = llm_client
    
    def analyze(self, alerts, metrics):
        """
        完整的根因分析流程
        """
        results = {
            "alerts": alerts,
            "metrics_analysis": {},
            "topology_analysis": {},
            "root_cause_candidates": [],
            "llm_analysis": None,
            "recommendations": []
        }
        
        # 1. 指标异常检测
        results["metrics_analysis"] = self._analyze_metrics(metrics)
        
        # 2. 拓扑分析
        alert_node = alerts[0]["host"] if alerts else None
        if alert_node:
            results["topology_analysis"] = self._analyze_topology(alert_node)
        
        # 3. 关联历史案例
        similar_cases = self._find_similar_cases(alerts)
        
        # 4. 生成候选根因
        results["root_cause_candidates"] = self._generate_candidates(
            results["metrics_analysis"],
            results["topology_analysis"],
            similar_cases
        )
        
        # 5. LLM 深度分析（可选）
        if self.llm_client:
            results["llm_analysis"] = self._llm_analyze(
                alerts,
                results["metrics_analysis"],
                results["root_cause_candidates"],
                similar_cases
            )
        
        # 6. 生成排查建议
        results["recommendations"] = self._generate_recommendations(
            results["root_cause_candidates"],
            similar_cases
        )
        
        return results
    
    def _analyze_metrics(self, metrics):
        """指标分析"""
        analysis = {}
        for metric_name, data in metrics.items():
            # 3σ 检测
            anomalies_3sigma = detect_anomaly_3sigma(data)
            # IQR 检测
            anomalies_iqr = detect_anomaly_iqr(data)
            # EWMA 检测
            anomalies_ewma = detect_anomaly_ewma(data)
            
            analysis[metric_name] = {
                "3sigma": anomalies_3sigma,
                "iqr": anomalies_iqr,
                "ewma": anomalies_ewma
            }
        return analysis
    
    def _analyze_topology(self, alert_node):
        """拓扑分析"""
        return random_walk_root_cause(self.topology, alert_node)
    
    def _find_similar_cases(self, alerts):
        """查找相似历史案例"""
        # 简单的关键词匹配
        alert_keywords = set()
        for alert in alerts:
            alert_keywords.update(alert["name"].split())
        
        similar = []
        for case in self.history_cases:
            case_keywords = set(case["title"].split() + case["tags"])
            overlap = alert_keywords & case_keywords
            if overlap:
                similar.append({
                    "case": case,
                    "overlap": overlap,
                    "score": len(overlap)
                })
        
        return sorted(similar, key=lambda x: x["score"], reverse=True)[:5]
    
    def _generate_candidates(self, metrics_analysis, topology_analysis, similar_cases):
        """生成根因候选"""
        candidates = []
        
        # 从拓扑分析获取
        for node in topology_analysis:
            if node["score"] > 0.1:
                candidates.append({
                    "source": "topology",
                    "node": node["node"],
                    "score": node["score"],
                    "description": f"拓扑随机游走得分: {node['score']:.2f}"
                })
        
        # 从指标分析获取
        for metric_name, analysis in metrics_analysis.items():
            if analysis["3sigma"] or analysis["iqr"]:
                candidates.append({
                    "source": "metrics",
                    "node": metric_name,
                    "score": 0.5,
                    "description": f"指标 {metric_name} 异常"
                })
        
        # 从历史案例获取
        for similar in similar_cases:
            candidates.append({
                "source": "history",
                "node": similar["case"]["root_cause"],
                "score": similar["score"] / 10,
                "description": f"相似案例: {similar['case']['title']}"
            })
        
        return sorted(candidates, key=lambda x: x["score"], reverse=True)
    
    def _llm_analyze(self, alerts, metrics_analysis, candidates, similar_cases):
        """LLM 分析"""
        if not self.llm_client:
            return None
        
        prompt = self._build_llm_prompt(alerts, metrics_analysis, candidates, similar_cases)
        return self.llm_client.complete(prompt)
    
    def _generate_recommendations(self, candidates, similar_cases):
        """生成排查建议"""
        recommendations = []
        
        for candidate in candidates[:3]:
            # 查找相似案例的解决方案
            for similar in similar_cases:
                if candidate["node"] in similar["case"]["root_cause"]:
                    recommendations.append({
                        "priority": "high",
                        "title": f"排查 {candidate['node']}",
                        "steps": [
                            f"检查 {candidate['node']} 状态",
                            "查看相关日志",
                            "参考案例: {similar['case']['title']}"
                        ],
                        "solution": similar["case"]["solution"]
                    })
        
        return recommendations
    
    def _build_llm_prompt(self, alerts, metrics_analysis, candidates, similar_cases):
        """构建 LLM Prompt"""
        return f"""你是一位运维专家。请分析以下故障：

【当前告警】
{alerts}

【指标分析】
{metrics_analysis}

【根因候选】
{candidates}

【相似历史案例】
{similar_cases}

请输出：
1. 告警摘要
2. 最可能的根因（排序）
3. 详细排查步骤
4. 恢复方案
"""
```

---

## 七、总结与建议

### 7.1 实施路线图

| 阶段 | 时间 | 目标 |
|------|------|------|
| **Phase 1** | 1-2 周 | 基础算法：3σ、IQR、时间窗口聚合 |
| **Phase 2** | 2-3 周 | 拓扑分析、告警关联规则 |
| **Phase 3** | 3-4 周 | 大模型结合、RAG |
| **Phase 4** | 持续 | 优化算法、机器学习 |

---

### 7.2 技术栈建议

| 组件 | 推荐技术 |
|------|----------|
| **数据存储** | MySQL + Redis |
| **时序数据** | Prometheus + VictoriaMetrics |
| **向量库** | Chroma / Milvus / pgvector |
| **大模型** | Qwen (私有化) / GPT-4 (云端) |
| **算法库** | NumPy, SciPy, scikit-learn, mlxtend |
| **图算法** | NetworkX, pgmpy |

---

### 7.3 注意事项

1. **数据质量**：确保指标、告警、拓扑数据的准确性
2. **可解释性**：优先选择可解释的算法，方便运维理解
3. **渐进式上线**：先上线简单规则，再逐步增加复杂算法
4. **反馈循环**：收集运维反馈，持续优化算法
5. **性能考虑**：实时分析需要考虑算法的计算效率

---

## 附录

### A. 参考资料
- 《运维监控系统实战》
- 《异常检测算法综述》
- 《贝叶斯网络与概率图模型》
- 《RAG：检索增强生成》

### B. 相关开源项目
- Prometheus Alertmanager（告警聚合）
- Netdata（实时监控）
- Jaeger（链路追踪）
- LangChain（LLM 应用开发）

---

**文档结束**
