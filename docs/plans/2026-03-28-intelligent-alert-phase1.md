# 智能告警模块 Phase 1 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现智能告警模块 Phase 1，包含基础告警功能、AI 诊断和前端页面。

**Architecture:** 后端使用 FastAPI + SQLAlchemy，告警评估引擎使用 APScheduler 定时调度，AI 诊断复用现有模型管理配置。前端使用 Vue 3 + Element Plus。

**Tech Stack:** Python FastAPI, SQLAlchemy, APScheduler, Vue 3, TypeScript, Element Plus

---

## 文件结构

### 后端新增/修改文件

```
backend/apps/alert/
├── models.py              # 新增 AlertEvent, DiagnosisReport, DiagnosisConversation 模型
├── schemas.py             # 新增对应的 Pydantic schemas
├── router.py              # 新增诊断相关 API
├── engine/
│   ├── __init__.py        # 新建目录
│   ├── evaluator.py       # 告警评估引擎
│   └── scheduler.py       # 调度器
└── diagnosis/
    ├── __init__.py        # 新建目录
    └── analyzer.py        # AI 诊断分析器
```

### 前端新增/修改文件

```
frontend/src/
├── api/
│   └── alert.ts           # 告警 API 接口
├── views/
│   └── monitor/
│       ├── Index.vue      # 智能监控入口（修改现有）
│       ├── AlertRules.vue # 告警规则管理
│       ├── AlertList.vue  # 告警列表
│       └── DiagnosisDialog.vue # AI 诊断对话框
└── router/
    └── index.ts           # 添加告警相关路由
```

---

## Task 1: 数据库模型更新

**Files:**
- Modify: `backend/apps/alert/models.py`

- [ ] **Step 1: 添加新模型到 models.py**

在 `backend/apps/alert/models.py` 文件末尾添加以下内容：

```python
class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="事件标题")
    severity = Column(String(50), nullable=False, comment="严重程度")
    alert_ids = Column(Text, nullable=True, comment="关联告警ID列表(JSON)")
    status = Column(String(50), default="active", comment="状态: active/resolved")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="恢复时间")


class DiagnosisReport(Base):
    __tablename__ = "diagnosis_reports"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=False, index=True, comment="告警ID")
    report = Column(Text, nullable=True, comment="诊断报告内容")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiagnosisConversation(Base):
    __tablename__ = "diagnosis_conversations"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=False, index=True, comment="告警ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    messages = Column(Text, nullable=True, comment="对话消息列表(JSON)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

- [ ] **Step 2: 创建数据库迁移脚本**

创建文件 `backend/apps/alert/migrations/add_alert_tables.py`：

```python
from sqlalchemy import text
from common.core.database import engine

def upgrade():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alert_events (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL COMMENT '事件标题',
                severity VARCHAR(50) NOT NULL COMMENT '严重程度',
                alert_ids TEXT COMMENT '关联告警ID列表(JSON)',
                status VARCHAR(50) DEFAULT 'active' COMMENT '状态',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME NULL COMMENT '恢复时间',
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS diagnosis_reports (
                id INT PRIMARY KEY AUTO_INCREMENT,
                alert_id INT NOT NULL COMMENT '告警ID',
                report TEXT COMMENT '诊断报告内容',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_alert_id (alert_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS diagnosis_conversations (
                id INT PRIMARY KEY AUTO_INCREMENT,
                alert_id INT NOT NULL COMMENT '告警ID',
                user_id INT NOT NULL COMMENT '用户ID',
                messages TEXT COMMENT '对话消息列表(JSON)',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_alert_id (alert_id),
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        conn.commit()
    print("数据库表创建成功！")

if __name__ == "__main__":
    upgrade()
```

- [ ] **Step 3: 运行迁移脚本**

Run: `cd backend && python -m apps.alert.migrations.add_alert_tables`
Expected: 输出 "数据库表创建成功！"

---

## Task 2: Pydantic Schemas 更新

**Files:**
- Modify: `backend/apps/alert/schemas.py`

- [ ] **Step 1: 添加新的 Schema 定义**

在 `backend/apps/alert/schemas.py` 文件末尾添加：

```python
from typing import List, Optional
from datetime import datetime


class AlertEventBase(BaseModel):
    title: str = Field(..., description="事件标题")
    severity: str = Field(..., description="严重程度")
    alert_ids: Optional[List[int]] = Field(None, description="关联告警ID列表")
    status: str = Field("active", description="状态")


class AlertEventCreate(AlertEventBase):
    pass


class AlertEventResponse(AlertEventBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiagnosisReportBase(BaseModel):
    alert_id: int = Field(..., description="告警ID")
    report: Optional[str] = Field(None, description="诊断报告")


class DiagnosisReportCreate(DiagnosisReportBase):
    pass


class DiagnosisReportResponse(DiagnosisReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DiagnosisChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")


class DiagnosisChatResponse(BaseModel):
    id: int
    alert_id: int
    message: str
    created_at: datetime


class DiagnosisContext(BaseModel):
    alert_id: int
    rule_name: str
    severity: str
    metric_value: Optional[float]
    threshold: Optional[float]
    message: Optional[str]
    created_at: datetime
```

---

## Task 3: 告警评估引擎

**Files:**
- Create: `backend/apps/alert/engine/__init__.py`
- Create: `backend/apps/alert/engine/evaluator.py`
- Create: `backend/apps/alert/engine/scheduler.py`

- [ ] **Step 1: 创建 engine 目录初始化文件**

创建文件 `backend/apps/alert/engine/__init__.py`：

```python
from .evaluator import AlertEvaluator
from .scheduler import AlertScheduler

__all__ = ["AlertEvaluator", "AlertScheduler"]
```

- [ ] **Step 2: 创建告警评估器**

创建文件 `backend/apps/alert/engine/evaluator.py`：

```python
import httpx
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from apps.alert.models import AlertRule, Alert
from apps.datasource.models import Datasource
import json


class AlertEvaluator:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_rule(self, rule: AlertRule) -> Optional[Alert]:
        datasource = self.db.query(Datasource).filter(Datasource.id == rule.datasource_id).first()
        if not datasource:
            print(f"数据源不存在: {rule.datasource_id}")
            return None

        metric_value = self._query_metric(datasource, rule.metric_query)
        if metric_value is None:
            return None

        triggered = self._check_condition(rule.condition_type, metric_value, float(rule.threshold) if rule.threshold else 0)

        if triggered:
            existing_alert = self.db.query(Alert).filter(
                Alert.rule_id == rule.id,
                Alert.resolved == False
            ).first()
            
            if existing_alert:
                existing_alert.metric_value = metric_value
                self.db.commit()
                return existing_alert

            alert = Alert(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                metric_value=metric_value,
                threshold=rule.threshold,
                message=f"{rule.name}: {metric_value} 触发阈值 {rule.threshold}",
                resolved=False,
                datasource_id=rule.datasource_id
            )
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            return alert
        else:
            existing_alert = self.db.query(Alert).filter(
                Alert.rule_id == rule.id,
                Alert.resolved == False
            ).first()
            
            if existing_alert:
                existing_alert.resolved = True
                existing_alert.resolved_at = datetime.now()
                self.db.commit()
            
            return None

    def _query_metric(self, datasource: Datasource, query: str) -> Optional[float]:
        try:
            if datasource.type == "prometheus":
                url = f"{datasource.url}/api/v1/query"
                params = {"query": query}
                
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                if data.get("status") == "success" and data.get("data", {}).get("result"):
                    results = data["data"]["result"]
                    if results:
                        value = results[0].get("value", [None, 0])[1]
                        return float(value)
                
                return None
            else:
                print(f"不支持的数据源类型: {datasource.type}")
                return None
        except Exception as e:
            print(f"查询指标失败: {e}")
            return None

    def _check_condition(self, condition_type: str, value: float, threshold: float) -> bool:
        if condition_type == "greater_than":
            return value > threshold
        elif condition_type == "less_than":
            return value < threshold
        elif condition_type == "equal_to":
            return value == threshold
        return False

    def evaluate_all_rules(self) -> List[Alert]:
        rules = self.db.query(AlertRule).filter(AlertRule.enabled == True).all()
        new_alerts = []
        
        for rule in rules:
            alert = self.evaluate_rule(rule)
            if alert:
                new_alerts.append(alert)
        
        return new_alerts


from datetime import datetime
```

- [ ] **Step 3: 创建调度器**

创建文件 `backend/apps/alert/engine/scheduler.py`：

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from common.core.database import SessionLocal
from .evaluator import AlertEvaluator
import logging

logger = logging.getLogger(__name__)


class AlertScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.evaluator = None

    def start(self):
        self.scheduler.start()
        self._add_jobs()
        logger.info("告警评估调度器已启动")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("告警评估调度器已停止")

    def _add_jobs(self):
        self.scheduler.add_job(
            self._evaluate_critical,
            IntervalTrigger(seconds=15),
            id="evaluate_critical",
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self._evaluate_warning,
            IntervalTrigger(seconds=30),
            id="evaluate_warning",
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self._evaluate_info,
            IntervalTrigger(seconds=120),
            id="evaluate_info",
            replace_existing=True
        )

    def _evaluate_critical(self):
        db = SessionLocal()
        try:
            evaluator = AlertEvaluator(db)
            from apps.alert.models import AlertRule
            rules = db.query(AlertRule).filter(
                AlertRule.enabled == True,
                AlertRule.severity == "critical"
            ).all()
            
            for rule in rules:
                evaluator.evaluate_rule(rule)
        except Exception as e:
            logger.error(f"评估 critical 规则失败: {e}")
        finally:
            db.close()

    def _evaluate_warning(self):
        db = SessionLocal()
        try:
            evaluator = AlertEvaluator(db)
            from apps.alert.models import AlertRule
            rules = db.query(AlertRule).filter(
                AlertRule.enabled == True,
                AlertRule.severity == "warning"
            ).all()
            
            for rule in rules:
                evaluator.evaluate_rule(rule)
        except Exception as e:
            logger.error(f"评估 warning 规则失败: {e}")
        finally:
            db.close()

    def _evaluate_info(self):
        db = SessionLocal()
        try:
            evaluator = AlertEvaluator(db)
            from apps.alert.models import AlertRule
            rules = db.query(AlertRule).filter(
                AlertRule.enabled == True,
                AlertRule.severity == "info"
            ).all()
            
            for rule in rules:
                evaluator.evaluate_rule(rule)
        except Exception as e:
            logger.error(f"评估 info 规则失败: {e}")
        finally:
            db.close()


alert_scheduler = AlertScheduler()
```

---

## Task 4: AI 诊断模块

**Files:**
- Create: `backend/apps/alert/diagnosis/__init__.py`
- Create: `backend/apps/alert/diagnosis/analyzer.py`

- [ ] **Step 1: 创建 diagnosis 目录初始化文件**

创建文件 `backend/apps/alert/diagnosis/__init__.py`：

```python
from .analyzer import DiagnosisAnalyzer

__all__ = ["DiagnosisAnalyzer"]
```

- [ ] **Step 2: 创建 AI 诊断分析器**

创建文件 `backend/apps/alert/diagnosis/analyzer.py`：

```python
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from apps.alert.models import Alert, DiagnosisReport, DiagnosisConversation
from apps.model.models import ModelConfig
from apps.model.services import ModelService
import httpx


class DiagnosisAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def _get_model_service(self) -> Optional[ModelService]:
        model_config = self.db.query(ModelConfig).filter(ModelConfig.is_default == True).first()
        if not model_config:
            model_config = self.db.query(ModelConfig).first()
        
        if not model_config:
            return None
        
        return ModelService(model_config)

    def _build_diagnosis_prompt(self, alert: Alert) -> str:
        prompt = f"""你是一个专业的运维诊断专家。请根据以下告警信息，生成诊断报告。

## 告警信息
- 规则名称: {alert.rule_name}
- 严重程度: {alert.severity}
- 当前指标值: {alert.metric_value}
- 阈值: {alert.threshold}
- 告警消息: {alert.message}
- 触发时间: {alert.created_at}

## 请输出以下内容：

### 1. 问题分析
简要分析这个告警表示什么问题。

### 2. 可能原因
列出 3-5 个可能的原因，按可能性排序。

### 3. 建议操作
列出具体的排查步骤和可能的解决方案。

### 4. 风险评估
评估如果不处理可能带来的影响。

请用中文回答，格式清晰。
"""
        return prompt

    def _build_chat_prompt(self, alert: Alert, messages: List[Dict], user_message: str) -> str:
        history = "\n".join([
            f"{'用户' if m['role'] == 'user' else '助手'}: {m['content']}"
            for m in messages
        ])
        
        prompt = f"""你是一个专业的运维诊断专家。用户正在针对一个告警进行深入诊断。

## 告警信息
- 规则名称: {alert.rule_name}
- 严重程度: {alert.severity}
- 当前指标值: {alert.metric_value}
- 阈值: {alert.threshold}
- 告警消息: {alert.message}

## 对话历史
{history if history else '无'}

## 用户最新问题
{user_message}

请用中文回答，简洁专业。
"""
        return prompt

    async def generate_diagnosis(self, alert_id: int) -> Optional[DiagnosisReport]:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None

        model_service = self._get_model_service()
        if not model_service:
            return DiagnosisReport(
                alert_id=alert_id,
                report="错误: 未配置默认模型，无法生成诊断报告。请先在模型管理中配置模型。"
            )

        prompt = self._build_diagnosis_prompt(alert)
        
        try:
            response = await model_service.chat(prompt)
            
            report = DiagnosisReport(
                alert_id=alert_id,
                report=response
            )
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception as e:
            return DiagnosisReport(
                alert_id=alert_id,
                report=f"诊断生成失败: {str(e)}"
            )

    async def chat(self, alert_id: int, user_id: int, user_message: str) -> Optional[Dict]:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None

        model_service = self._get_model_service()
        if not model_service:
            return {
                "message": "错误: 未配置默认模型，无法进行对话。请先在模型管理中配置模型。"
            }

        conversation = self.db.query(DiagnosisConversation).filter(
            DiagnosisConversation.alert_id == alert_id,
            DiagnosisConversation.user_id == user_id
        ).first()

        if not conversation:
            conversation = DiagnosisConversation(
                alert_id=alert_id,
                user_id=user_id,
                messages=json.dumps([])
            )
            self.db.add(conversation)
            self.db.commit()

        messages = json.loads(conversation.messages) if conversation.messages else []
        messages.append({"role": "user", "content": user_message})

        prompt = self._build_chat_prompt(alert, messages, user_message)
        
        try:
            response = await model_service.chat(prompt)
            
            messages.append({"role": "assistant", "content": response})
            conversation.messages = json.dumps(messages)
            self.db.commit()

            return {
                "id": conversation.id,
                "alert_id": alert_id,
                "message": response,
                "created_at": conversation.updated_at or conversation.created_at
            }
        except Exception as e:
            return {
                "message": f"对话失败: {str(e)}"
            }

    def get_conversation(self, alert_id: int, user_id: int) -> List[Dict]:
        conversation = self.db.query(DiagnosisConversation).filter(
            DiagnosisConversation.alert_id == alert_id,
            DiagnosisConversation.user_id == user_id
        ).first()

        if not conversation or not conversation.messages:
            return []

        return json.loads(conversation.messages)
```

---

## Task 5: 后端 API 路由更新

**Files:**
- Modify: `backend/apps/alert/router.py`

- [ ] **Step 1: 添加诊断相关 API**

在 `backend/apps/alert/router.py` 文件末尾添加：

```python
from .models import AlertEvent, DiagnosisReport, DiagnosisConversation
from .schemas import (
    AlertEventCreate,
    AlertEventResponse,
    DiagnosisReportResponse,
    DiagnosisChatRequest,
    DiagnosisChatResponse
)
from .diagnosis.analyzer import DiagnosisAnalyzer
from datetime import datetime


# ==================== 告警事件 API ====================

def alert_event_to_dict(event: AlertEvent) -> dict:
    return {
        "id": event.id,
        "title": event.title,
        "severity": event.severity,
        "alert_ids": json.loads(event.alert_ids) if event.alert_ids else [],
        "status": event.status,
        "created_at": event.created_at,
        "resolved_at": event.resolved_at,
    }


@router.get("/events", response_model=List[AlertEventResponse])
def get_alert_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status: Optional[str] = None,
    limit: int = 100
):
    query = db.query(AlertEvent)
    if status:
        query = query.filter(AlertEvent.status == status)
    events = query.order_by(AlertEvent.created_at.desc()).limit(limit).all()
    return [alert_event_to_dict(e) for e in events]


@router.get("/events/{event_id}", response_model=AlertEventResponse)
def get_alert_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    event = db.query(AlertEvent).filter(AlertEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="告警事件不存在")
    return alert_event_to_dict(event)


# ==================== AI 诊断 API ====================

@router.post("/{alert_id}/diagnose", response_model=DiagnosisReportResponse)
async def diagnose_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    analyzer = DiagnosisAnalyzer(db)
    report = await analyzer.generate_diagnosis(alert_id)
    if not report:
        raise HTTPException(status_code=404, detail="告警不存在")
    
    return {
        "id": report.id,
        "alert_id": report.alert_id,
        "report": report.report,
        "created_at": report.created_at
    }


@router.get("/{alert_id}/diagnosis", response_model=List[DiagnosisReportResponse])
def get_diagnosis_reports(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.alert_id == alert_id
    ).order_by(DiagnosisReport.created_at.desc()).all()
    
    return [
        {
            "id": r.id,
            "alert_id": r.alert_id,
            "report": r.report,
            "created_at": r.created_at
        }
        for r in reports
    ]


@router.post("/{alert_id}/chat")
async def chat_diagnosis(
    alert_id: int,
    request: DiagnosisChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    analyzer = DiagnosisAnalyzer(db)
    result = await analyzer.chat(alert_id, current_user.id, request.message)
    if not result:
        raise HTTPException(status_code=404, detail="告警不存在")
    
    return result


@router.get("/{alert_id}/conversation")
def get_conversation(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    analyzer = DiagnosisAnalyzer(db)
    messages = analyzer.get_conversation(alert_id, current_user.id)
    return {"messages": messages}
```

- [ ] **Step 2: 添加必要的导入**

在 `backend/apps/alert/router.py` 文件顶部添加：

```python
import json
from typing import Optional
```

---

## Task 6: 集成调度器到主应用

**Files:**
- Modify: `backend/main.py`

- [ ] **Step 1: 启动告警调度器**

在 `backend/main.py` 中添加调度器启动逻辑：

找到 `app = FastAPI(...)` 之后，添加：

```python
from apps.alert.engine.scheduler import alert_scheduler

@app.on_event("startup")
async def startup_event():
    alert_scheduler.start()
    print("告警评估调度器已启动")

@app.on_event("shutdown")
async def shutdown_event():
    alert_scheduler.stop()
    print("告警评估调度器已停止")
```

---

## Task 7: 前端 API 接口

**Files:**
- Create: `frontend/src/api/alert.ts`

- [ ] **Step 1: 创建告警 API 接口文件**

创建文件 `frontend/src/api/alert.ts`：

```typescript
import request from './index'

export interface AlertRule {
  id: number
  name: string
  description?: string
  datasource_id: number
  datasource_type: string
  metric_query: string
  condition_type: string
  threshold?: number
  severity: string
  evaluation_interval: number
  enabled: boolean
  created_at: string
  updated_at?: string
}

export interface Alert {
  id: number
  rule_id: number
  rule_name?: string
  severity: string
  metric_value?: number
  threshold?: number
  message?: string
  resolved: boolean
  resolved_at?: string
  datasource_id?: number
  created_at: string
}

export interface AlertEvent {
  id: number
  title: string
  severity: string
  alert_ids: number[]
  status: string
  created_at: string
  resolved_at?: string
}

export interface DiagnosisReport {
  id: number
  alert_id: number
  report: string
  created_at: string
}

export interface AlertStats {
  total: number
  critical: number
  warning: number
  info: number
  resolved: number
  active: number
}

export const alertApi = {
  getRules: (enabledOnly = false) => 
    request.get<AlertRule[]>('/alerts/rules', { params: { enabled_only: enabledOnly } }),
  
  getRule: (id: number) => 
    request.get<AlertRule>(`/alerts/rules/${id}`),
  
  createRule: (data: Partial<AlertRule>) => 
    request.post<AlertRule>('/alerts/rules', data),
  
  updateRule: (id: number, data: Partial<AlertRule>) => 
    request.put<AlertRule>(`/alerts/rules/${id}`, data),
  
  deleteRule: (id: number) => 
    request.delete(`/alerts/rules/${id}`),
  
  testRule: (id: number, testValue: number) => 
    request.post(`/alerts/rules/${id}/test`, { test_value: testValue }),
  
  getAlerts: (params?: { resolved_only?: boolean; active_only?: boolean; limit?: number }) => 
    request.get<Alert[]>('/alerts', { params }),
  
  getAlert: (id: number) => 
    request.get<Alert>(`/alerts/${id}`),
  
  resolveAlert: (id: number) => 
    request.put<Alert>(`/alerts/${id}/resolve`),
  
  getStats: () => 
    request.get<AlertStats>('/alerts/stats'),
  
  getEvents: (status?: string, limit = 100) => 
    request.get<AlertEvent[]>('/alerts/events', { params: { status, limit } }),
  
  getEvent: (id: number) => 
    request.get<AlertEvent>(`/alerts/events/${id}`),
  
  diagnose: (alertId: number) => 
    request.post<DiagnosisReport>(`/alerts/${alertId}/diagnose`),
  
  getDiagnosis: (alertId: number) => 
    request.get<DiagnosisReport[]>(`/alerts/${alertId}/diagnosis`),
  
  chat: (alertId: number, message: string) => 
    request.post(`/alerts/${alertId}/chat`, { message }),
  
  getConversation: (alertId: number) => 
    request.get<{ messages: Array<{ role: string; content: string }> }>(`/alerts/${alertId}/conversation`),
}
```

---

## Task 8: 前端路由配置

**Files:**
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: 添加告警相关路由**

在 `frontend/src/router/index.ts` 的 children 数组中添加：

```typescript
      {
        path: 'monitor/rules',
        name: 'AlertRules',
        component: () => import('../views/monitor/AlertRules.vue'),
        meta: { title: '告警规则', requiresAuth: true }
      },
      {
        path: 'monitor/alerts',
        name: 'AlertList',
        component: () => import('../views/monitor/AlertList.vue'),
        meta: { title: '告警列表', requiresAuth: true }
      },
```

---

## Task 9: 告警规则管理页面

**Files:**
- Create: `frontend/src/views/monitor/AlertRules.vue`

- [ ] **Step 1: 创建告警规则管理页面**

创建文件 `frontend/src/views/monitor/AlertRules.vue`：

```vue
<template>
  <div class="alert-rules">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>告警规则管理</span>
          <el-button type="primary" @click="showDialog()">新增规则</el-button>
        </div>
      </template>

      <el-table :data="rules" v-loading="loading" stripe>
        <el-table-column prop="name" label="规则名称" width="200" />
        <el-table-column prop="datasource_type" label="数据源类型" width="120" />
        <el-table-column prop="metric_query" label="指标查询" show-overflow-tooltip />
        <el-table-column prop="condition_type" label="条件" width="100">
          <template #default="{ row }">
            {{ conditionMap[row.condition_type] || row.condition_type }}
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="80" />
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="severityMap[row.severity]">{{ severityLabelMap[row.severity] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="toggleEnabled(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="testRule(row)">测试</el-button>
            <el-button size="small" @click="showDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingRule ? '编辑规则' : '新增规则'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="数据源ID" prop="datasource_id">
          <el-input-number v-model="form.datasource_id" :min="1" />
        </el-form-item>
        <el-form-item label="数据源类型" prop="datasource_type">
          <el-select v-model="form.datasource_type" placeholder="请选择数据源类型">
            <el-option label="Prometheus" value="prometheus" />
            <el-option label="Zabbix" value="zabbix" />
          </el-select>
        </el-form-item>
        <el-form-item label="指标查询" prop="metric_query">
          <el-input v-model="form.metric_query" placeholder="例如: cpu_usage{host='web-01'}" />
        </el-form-item>
        <el-form-item label="条件类型" prop="condition_type">
          <el-select v-model="form.condition_type" placeholder="请选择条件类型">
            <el-option label="大于" value="greater_than" />
            <el-option label="小于" value="less_than" />
            <el-option label="等于" value="equal_to" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值" prop="threshold">
          <el-input-number v-model="form.threshold" :precision="2" />
        </el-form-item>
        <el-form-item label="严重程度" prop="severity">
          <el-select v-model="form.severity" placeholder="请选择严重程度">
            <el-option label="严重" value="critical" />
            <el-option label="警告" value="warning" />
            <el-option label="信息" value="info" />
          </el-select>
        </el-form-item>
        <el-form-item label="评估间隔" prop="evaluation_interval">
          <el-input-number v-model="form.evaluation_interval" :min="10" :max="3600" /> 秒
        </el-form-item>
        <el-form-item label="启用" prop="enabled">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="testDialogVisible" title="测试规则" width="400px">
      <el-form label-width="80px">
        <el-form-item label="测试值">
          <el-input-number v-model="testValue" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="testDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="runTest" :loading="testing">测试</el-button>
      </template>
      <div v-if="testResult" class="test-result">
        <el-divider />
        <p><strong>结果:</strong> {{ testResult.triggered ? '触发告警' : '未触发' }}</p>
        <p><strong>消息:</strong> {{ testResult.message }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { alertApi, AlertRule } from '@/api/alert'

const loading = ref(false)
const rules = ref<AlertRule[]>([])
const dialogVisible = ref(false)
const editingRule = ref<AlertRule | null>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const testDialogVisible = ref(false)
const testingRule = ref<AlertRule | null>(null)
const testValue = ref(0)
const testing = ref(false)
const testResult = ref<any>(null)

const form = reactive({
  name: '',
  description: '',
  datasource_id: 1,
  datasource_type: 'prometheus',
  metric_query: '',
  condition_type: 'greater_than',
  threshold: 80,
  severity: 'warning',
  evaluation_interval: 30,
  enabled: true
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  datasource_id: [{ required: true, message: '请输入数据源ID', trigger: 'blur' }],
  datasource_type: [{ required: true, message: '请选择数据源类型', trigger: 'change' }],
  metric_query: [{ required: true, message: '请输入指标查询', trigger: 'blur' }],
  condition_type: [{ required: true, message: '请选择条件类型', trigger: 'change' }],
  severity: [{ required: true, message: '请选择严重程度', trigger: 'change' }]
}

const conditionMap: Record<string, string> = {
  greater_than: '大于',
  less_than: '小于',
  equal_to: '等于'
}

const severityMap: Record<string, string> = {
  critical: 'danger',
  warning: 'warning',
  info: 'info'
}

const severityLabelMap: Record<string, string> = {
  critical: '严重',
  warning: '警告',
  info: '信息'
}

const loadRules = async () => {
  loading.value = true
  try {
    rules.value = await alertApi.getRules()
  } catch (error) {
    ElMessage.error('加载规则列表失败')
  } finally {
    loading.value = false
  }
}

const showDialog = (rule?: AlertRule) => {
  editingRule.value = rule || null
  if (rule) {
    Object.assign(form, rule)
  } else {
    Object.assign(form, {
      name: '',
      description: '',
      datasource_id: 1,
      datasource_type: 'prometheus',
      metric_query: '',
      condition_type: 'greater_than',
      threshold: 80,
      severity: 'warning',
      evaluation_interval: 30,
      enabled: true
    })
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (editingRule.value) {
        await alertApi.updateRule(editingRule.value.id, form)
        ElMessage.success('更新成功')
      } else {
        await alertApi.createRule(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadRules()
    } catch (error) {
      ElMessage.error('操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const toggleEnabled = async (rule: AlertRule) => {
  try {
    await alertApi.updateRule(rule.id, { enabled: rule.enabled })
    ElMessage.success('状态更新成功')
  } catch (error) {
    rule.enabled = !rule.enabled
    ElMessage.error('状态更新失败')
  }
}

const deleteRule = async (rule: AlertRule) => {
  try {
    await ElMessageBox.confirm('确定要删除该规则吗？', '提示', { type: 'warning' })
    await alertApi.deleteRule(rule.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const testRule = (rule: AlertRule) => {
  testingRule.value = rule
  testValue.value = rule.threshold || 0
  testResult.value = null
  testDialogVisible.value = true
}

const runTest = async () => {
  if (!testingRule.value) return
  testing.value = true
  try {
    testResult.value = await alertApi.testRule(testingRule.value.id, testValue.value)
  } catch (error) {
    ElMessage.error('测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.alert-rules {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-result {
  margin-top: 10px;
}
</style>
```

---

## Task 10: 告警列表页面

**Files:**
- Create: `frontend/src/views/monitor/AlertList.vue`

- [ ] **Step 1: 创建告警列表页面**

创建文件 `frontend/src/views/monitor/AlertList.vue`：

```vue
<template>
  <div class="alert-list">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总告警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-item critical">
            <div class="stat-value">{{ stats.critical }}</div>
            <div class="stat-label">严重</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-item warning">
            <div class="stat-value">{{ stats.warning }}</div>
            <div class="stat-label">警告</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-item info">
            <div class="stat-value">{{ stats.info }}</div>
            <div class="stat-label">信息</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-item active">
            <div class="stat-value">{{ stats.active }}</div>
            <div class="stat-label">活跃</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-item resolved">
            <div class="stat-value">{{ stats.resolved }}</div>
            <div class="stat-label">已恢复</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="alert-card">
      <template #header>
        <div class="card-header">
          <span>告警列表</span>
          <div class="filter">
            <el-radio-group v-model="filter" @change="loadAlerts">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="active">活跃</el-radio-button>
              <el-radio-button label="resolved">已恢复</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <el-table :data="alerts" v-loading="loading" stripe>
        <el-table-column prop="rule_name" label="规则名称" width="200" />
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="severityMap[row.severity]">{{ severityLabelMap[row.severity] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metric_value" label="指标值" width="100" />
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column prop="message" label="告警消息" show-overflow-tooltip />
        <el-table-column prop="resolved" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.resolved ? 'success' : 'danger'">
              {{ row.resolved ? '已恢复' : '活跃' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="触发时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="diagnose(row)" :disabled="row.resolved">
              AI 诊断
            </el-button>
            <el-button size="small" type="success" @click="resolve(row)" :disabled="row.resolved">
              恢复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <DiagnosisDialog 
      v-model="diagnosisVisible" 
      :alert="selectedAlert" 
      @close="diagnosisVisible = false" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { alertApi, Alert, AlertStats } from '@/api/alert'
import DiagnosisDialog from './DiagnosisDialog.vue'

const loading = ref(false)
const alerts = ref<Alert[]>([])
const stats = ref<AlertStats>({
  total: 0,
  critical: 0,
  warning: 0,
  info: 0,
  resolved: 0,
  active: 0
})
const filter = ref('')

const diagnosisVisible = ref(false)
const selectedAlert = ref<Alert | null>(null)

const severityMap: Record<string, string> = {
  critical: 'danger',
  warning: 'warning',
  info: 'info'
}

const severityLabelMap: Record<string, string> = {
  critical: '严重',
  warning: '警告',
  info: '信息'
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

const loadStats = async () => {
  try {
    stats.value = await alertApi.getStats()
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const loadAlerts = async () => {
  loading.value = true
  try {
    const params: any = { limit: 100 }
    if (filter.value === 'active') {
      params.active_only = true
    } else if (filter.value === 'resolved') {
      params.resolved_only = true
    }
    alerts.value = await alertApi.getAlerts(params)
  } catch (error) {
    ElMessage.error('加载告警列表失败')
  } finally {
    loading.value = false
  }
}

const diagnose = (alert: Alert) => {
  selectedAlert.value = alert
  diagnosisVisible.value = true
}

const resolve = async (alert: Alert) => {
  try {
    await ElMessageBox.confirm('确定要标记该告警为已恢复吗？', '提示', { type: 'info' })
    await alertApi.resolveAlert(alert.id)
    ElMessage.success('已标记为恢复')
    loadAlerts()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  loadStats()
  loadAlerts()
})
</script>

<style scoped>
.alert-list {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.stat-item.critical .stat-value { color: #f56c6c; }
.stat-item.warning .stat-value { color: #e6a23c; }
.stat-item.info .stat-value { color: #909399; }
.stat-item.active .stat-value { color: #f56c6c; }
.stat-item.resolved .stat-value { color: #67c23a; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-card {
  margin-top: 0;
}
</style>
```

---

## Task 11: AI 诊断对话框组件

**Files:**
- Create: `frontend/src/views/monitor/DiagnosisDialog.vue`

- [ ] **Step 1: 创建 AI 诊断对话框组件**

创建文件 `frontend/src/views/monitor/DiagnosisDialog.vue`：

```vue
<template>
  <el-dialog 
    :model-value="modelValue" 
    @update:model-value="$emit('update:modelValue', $event)"
    title="AI 智能诊断" 
    width="700px"
    @open="handleOpen"
  >
    <div class="diagnosis-content">
      <div class="alert-info" v-if="alert">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="规则名称">{{ alert.rule_name }}</el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="severityMap[alert.severity]">{{ severityLabelMap[alert.severity] }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="指标值">{{ alert.metric_value }}</el-descriptions-item>
          <el-descriptions-item label="阈值">{{ alert.threshold }}</el-descriptions-item>
          <el-descriptions-item label="告警消息" :span="2">{{ alert.message }}</el-descriptions-item>
          <el-descriptions-item label="触发时间" :span="2">{{ formatTime(alert.created_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="diagnosis-section" v-if="report">
        <h4>诊断报告</h4>
        <div class="report-content" v-html="formatReport(report.report)"></div>
      </div>

      <div class="chat-section">
        <h4>继续对话</h4>
        <div class="chat-messages" ref="messagesRef">
          <div 
            v-for="(msg, index) in messages" 
            :key="index" 
            :class="['message', msg.role]"
          >
            <div class="message-content">{{ msg.content }}</div>
          </div>
        </div>
        <div class="chat-input">
          <el-input 
            v-model="userInput" 
            placeholder="输入问题继续诊断..." 
            @keyup.enter="sendMessage"
          >
            <template #append>
              <el-button @click="sendMessage" :loading="sending">发送</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="primary" @click="generateDiagnosis" :loading="generating">
        重新生成诊断
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { alertApi, Alert, DiagnosisReport } from '@/api/alert'

const props = defineProps<{
  modelValue: boolean
  alert: Alert | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}>()

const report = ref<DiagnosisReport | null>(null)
const messages = ref<Array<{ role: string; content: string }>>([])
const userInput = ref('')
const sending = ref(false)
const generating = ref(false)
const messagesRef = ref<HTMLElement | null>(null)

const severityMap: Record<string, string> = {
  critical: 'danger',
  warning: 'warning',
  info: 'info'
}

const severityLabelMap: Record<string, string> = {
  critical: '严重',
  warning: '警告',
  info: '信息'
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

const formatReport = (text: string) => {
  return text.replace(/\n/g, '<br>').replace(/##\s*(.+)/g, '<h4>$1</h4>')
}

const handleOpen = async () => {
  if (!props.alert) return
  
  report.value = null
  messages.value = []
  
  try {
    const reports = await alertApi.getDiagnosis(props.alert.id)
    if (reports.length > 0) {
      report.value = reports[0]
    }
    
    const conversation = await alertApi.getConversation(props.alert.id)
    messages.value = conversation.messages || []
  } catch (error) {
    console.error('加载诊断信息失败', error)
  }
}

const generateDiagnosis = async () => {
  if (!props.alert) return
  
  generating.value = true
  try {
    report.value = await alertApi.diagnose(props.alert.id)
    ElMessage.success('诊断报告已生成')
  } catch (error) {
    ElMessage.error('生成诊断失败')
  } finally {
    generating.value = false
  }
}

const sendMessage = async () => {
  if (!props.alert || !userInput.value.trim()) return
  
  const message = userInput.value.trim()
  userInput.value = ''
  
  messages.value.push({ role: 'user', content: message })
  
  sending.value = true
  try {
    const result = await alertApi.chat(props.alert.id, message)
    messages.value.push({ role: 'assistant', content: result.message })
    
    nextTick(() => {
      if (messagesRef.value) {
        messagesRef.value.scrollTop = messagesRef.value.scrollHeight
      }
    })
  } catch (error) {
    ElMessage.error('对话失败')
    messages.value.pop()
  } finally {
    sending.value = false
  }
}

watch(() => props.modelValue, (val) => {
  if (val) {
    handleOpen()
  }
})
</script>

<style scoped>
.diagnosis-content {
  max-height: 60vh;
  overflow-y: auto;
}

.alert-info {
  margin-bottom: 20px;
}

.diagnosis-section, .chat-section {
  margin-top: 20px;
}

.diagnosis-section h4, .chat-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.report-content {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  line-height: 1.6;
}

.chat-messages {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
  background: #fafafa;
}

.message {
  margin-bottom: 10px;
}

.message.user {
  text-align: right;
}

.message.assistant {
  text-align: left;
}

.message-content {
  display: inline-block;
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message.user .message-content {
  background: #409eff;
  color: #fff;
}

.chat-input {
  margin-top: 10px;
}
</style>
```

---

## Task 12: 更新监控入口页面

**Files:**
- Modify: `frontend/src/views/monitor/Index.vue`

- [ ] **Step 1: 更新监控入口页面**

修改文件 `frontend/src/views/monitor/Index.vue`：

```vue
<template>
  <div class="monitor-index">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="告警列表" name="alerts">
        <AlertList />
      </el-tab-pane>
      <el-tab-pane label="告警规则" name="rules">
        <AlertRules />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AlertList from './AlertList.vue'
import AlertRules from './AlertRules.vue'

const router = useRouter()
const route = useRoute()
const activeTab = ref('alerts')

const handleTabClick = (tab: any) => {
  if (tab.paneName === 'rules') {
    router.push('/monitor/rules')
  } else {
    router.push('/monitor/alerts')
  }
}
</script>

<style scoped>
.monitor-index {
  padding: 20px;
}
</style>
```

---

## Task 13: 创建迁移目录

**Files:**
- Create: `backend/apps/alert/migrations/__init__.py`

- [ ] **Step 1: 创建迁移目录初始化文件**

创建文件 `backend/apps/alert/migrations/__init__.py`：

```python
```

---

## 自检清单

- [x] Spec coverage: 所有设计文档中的功能都有对应任务
- [x] Placeholder scan: 无 TBD、TODO 等占位符
- [x] Type consistency: 前后端类型定义一致
