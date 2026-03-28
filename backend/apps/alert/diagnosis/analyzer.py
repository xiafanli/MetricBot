import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import httpx

from apps.alert.models import Alert, DiagnosisReport, DiagnosisConversation
from apps.model.models import Model


class DiagnosisAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def _get_default_model(self) -> Optional[Model]:
        model = self.db.query(Model).filter(
            Model.is_default == True,
            Model.is_enabled == True
        ).first()
        
        if not model:
            model = self.db.query(Model).filter(Model.is_enabled == True).first()
        
        return model

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

    async def _call_model(self, prompt: str, model: Model) -> str:
        if not model.api_domain:
            return "错误: 模型未配置 API 地址"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if model.api_key:
            headers["Authorization"] = f"Bearer {model.api_key}"
        
        config = json.loads(model.config) if model.config else {}
        
        payload = {
            "model": model.base_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 2000)
        }
        
        url = f"{model.api_domain.rstrip('/')}/chat/completions"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0].get("message", {}).get("content", "")
                
                return "错误: 模型返回格式异常"
        except httpx.TimeoutException:
            return "错误: 模型调用超时"
        except httpx.HTTPStatusError as e:
            return f"错误: 模型调用失败 - {e.response.status_code}"
        except Exception as e:
            return f"错误: {str(e)}"

    async def generate_diagnosis(self, alert_id: int) -> Optional[DiagnosisReport]:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None

        model = self._get_default_model()
        if not model:
            return DiagnosisReport(
                alert_id=alert_id,
                report="错误: 未配置可用模型，无法生成诊断报告。请先在模型管理中配置模型。"
            )

        prompt = self._build_diagnosis_prompt(alert)
        response = await self._call_model(prompt, model)
        
        report = DiagnosisReport(
            alert_id=alert_id,
            report=response
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    async def chat(self, alert_id: int, user_id: int, user_message: str) -> Optional[Dict]:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None

        model = self._get_default_model()
        if not model:
            return {
                "message": "错误: 未配置可用模型，无法进行对话。请先在模型管理中配置模型。"
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
        response = await self._call_model(prompt, model)
        
        messages.append({"role": "assistant", "content": response})
        conversation.messages = json.dumps(messages)
        self.db.commit()

        return {
            "id": conversation.id,
            "alert_id": alert_id,
            "message": response,
            "created_at": conversation.updated_at or conversation.created_at
        }

    def get_conversation(self, alert_id: int, user_id: int) -> List[Dict]:
        conversation = self.db.query(DiagnosisConversation).filter(
            DiagnosisConversation.alert_id == alert_id,
            DiagnosisConversation.user_id == user_id
        ).first()

        if not conversation or not conversation.messages:
            return []

        return json.loads(conversation.messages)
