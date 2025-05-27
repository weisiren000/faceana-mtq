"""
数据模型类
定义标准化的数据结构和验证规则
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# 配置日志
logger = logging.getLogger(__name__)


class EmotionCategory(Enum):
    """情绪类别枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EmotionIntensity(Enum):
    """情绪强度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AgentType(Enum):
    """智能体类型枚举"""
    DSA = "DSA"  # Data Sentiment Analysis
    VSA = "VSA"  # Visual Sentiment Analysis
    JSA = "JSA"  # Joint Sentiment Analysis


@dataclass
class EmotionResult:
    """情绪分析结果数据模型"""
    agent: str
    timestamp: str
    emotion_category: str
    dominant_emotion: str
    polarity_score: float
    confidence: float
    intensity: str
    reliability: str
    summary: str
    raw_data: Optional[Dict] = None
    
    def __post_init__(self):
        """数据验证"""
        # 验证极性分数范围
        if not -1.0 <= self.polarity_score <= 1.0:
            logger.warning(f"极性分数超出范围: {self.polarity_score}")
            self.polarity_score = max(-1.0, min(1.0, self.polarity_score))
            
        # 验证置信度范围
        if not 0.0 <= self.confidence <= 1.0:
            logger.warning(f"置信度超出范围: {self.confidence}")
            self.confidence = max(0.0, min(1.0, self.confidence))
            
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmotionResult':
        """从字典创建实例"""
        return cls(**data)
        
    def is_positive(self) -> bool:
        """是否为积极情绪"""
        return self.emotion_category == EmotionCategory.POSITIVE.value
        
    def is_negative(self) -> bool:
        """是否为消极情绪"""
        return self.emotion_category == EmotionCategory.NEGATIVE.value
        
    def is_neutral(self) -> bool:
        """是否为中性情绪"""
        return self.emotion_category == EmotionCategory.NEUTRAL.value
        
    def get_intensity_level(self) -> int:
        """获取强度等级 (1-3)"""
        intensity_map = {
            EmotionIntensity.LOW.value: 1,
            EmotionIntensity.MEDIUM.value: 2,
            EmotionIntensity.HIGH.value: 3
        }
        return intensity_map.get(self.intensity, 1)


@dataclass
class ConsistencyAnalysis:
    """一致性分析数据模型"""
    emotion_match: bool
    category_match: bool
    polarity_consistency: float
    confidence_consistency: float
    consistency_score: float
    consistency_level: str
    consistency_label: str
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConsistencyAnalysis':
        """从字典创建实例"""
        return cls(**data)
        
    def is_high_consistency(self) -> bool:
        """是否高一致性"""
        return self.consistency_score >= 0.8
        
    def is_low_consistency(self) -> bool:
        """是否低一致性"""
        return self.consistency_score < 0.5


@dataclass
class FinalJudgment:
    """最终判定数据模型"""
    emotion_category: str
    dominant_emotion: str
    polarity_score: float
    confidence: float
    intensity: str
    reliability: str
    summary: str
    contributing_agents: List[str]
    consistency_analysis: ConsistencyAnalysis
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = asdict(self)
        result['consistency_analysis'] = self.consistency_analysis.to_dict()
        return result
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'FinalJudgment':
        """从字典创建实例"""
        consistency_data = data.pop('consistency_analysis')
        consistency = ConsistencyAnalysis.from_dict(consistency_data)
        return cls(consistency_analysis=consistency, **data)


@dataclass
class AnalysisWorkflow:
    """分析工作流数据模型"""
    workflow_id: str
    workflow_type: str
    start_time: str
    end_time: Optional[str]
    status: str
    steps_completed: int
    total_steps: int
    agent_results: Dict[str, Optional[EmotionResult]]
    final_judgment: Optional[FinalJudgment]
    error_messages: List[str]
    
    def __post_init__(self):
        """初始化后处理"""
        if self.end_time is None and self.status == "completed":
            self.end_time = datetime.now().isoformat()
            
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = asdict(self)
        
        # 转换agent_results
        agent_results_dict = {}
        for agent, emotion_result in self.agent_results.items():
            if emotion_result:
                agent_results_dict[agent] = emotion_result.to_dict()
            else:
                agent_results_dict[agent] = None
        result['agent_results'] = agent_results_dict
        
        # 转换final_judgment
        if self.final_judgment:
            result['final_judgment'] = self.final_judgment.to_dict()
            
        return result
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisWorkflow':
        """从字典创建实例"""
        # 转换agent_results
        agent_results = {}
        for agent, result_data in data.get('agent_results', {}).items():
            if result_data:
                agent_results[agent] = EmotionResult.from_dict(result_data)
            else:
                agent_results[agent] = None
        data['agent_results'] = agent_results
        
        # 转换final_judgment
        if data.get('final_judgment'):
            data['final_judgment'] = FinalJudgment.from_dict(data['final_judgment'])
            
        return cls(**data)
        
    def add_agent_result(self, agent: str, result: EmotionResult):
        """添加智能体结果"""
        self.agent_results[agent] = result
        
    def set_final_judgment(self, judgment: FinalJudgment):
        """设置最终判定"""
        self.final_judgment = judgment
        
    def add_error(self, error_message: str):
        """添加错误信息"""
        self.error_messages.append(error_message)
        
    def mark_completed(self):
        """标记为完成"""
        self.status = "completed"
        self.end_time = datetime.now().isoformat()
        
    def mark_failed(self, error_message: str):
        """标记为失败"""
        self.status = "failed"
        self.end_time = datetime.now().isoformat()
        self.add_error(error_message)
        
    def get_duration(self) -> Optional[float]:
        """获取执行时长（秒）"""
        if not self.end_time:
            return None
            
        try:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            return (end - start).total_seconds()
        except Exception:
            return None
            
    def get_progress(self) -> float:
        """获取进度百分比"""
        if self.total_steps == 0:
            return 0.0
        return self.steps_completed / self.total_steps


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_emotion_result(data: Dict) -> bool:
        """验证情绪结果数据"""
        required_fields = [
            'agent', 'timestamp', 'emotion_category', 'dominant_emotion',
            'polarity_score', 'confidence', 'intensity', 'reliability', 'summary'
        ]
        
        # 检查必需字段
        for field in required_fields:
            if field not in data:
                logger.error(f"缺少必需字段: {field}")
                return False
                
        # 验证数值范围
        if not -1.0 <= data['polarity_score'] <= 1.0:
            logger.error(f"极性分数超出范围: {data['polarity_score']}")
            return False
            
        if not 0.0 <= data['confidence'] <= 1.0:
            logger.error(f"置信度超出范围: {data['confidence']}")
            return False
            
        # 验证枚举值
        valid_categories = [e.value for e in EmotionCategory]
        if data['emotion_category'] not in valid_categories:
            logger.error(f"无效的情绪类别: {data['emotion_category']}")
            return False
            
        valid_intensities = [e.value for e in EmotionIntensity]
        if data['intensity'] not in valid_intensities:
            logger.error(f"无效的情绪强度: {data['intensity']}")
            return False
            
        return True
        
    @staticmethod
    def validate_workflow(data: Dict) -> bool:
        """验证工作流数据"""
        required_fields = [
            'workflow_id', 'workflow_type', 'start_time', 'status',
            'steps_completed', 'total_steps', 'agent_results', 'error_messages'
        ]
        
        for field in required_fields:
            if field not in data:
                logger.error(f"工作流缺少必需字段: {field}")
                return False
                
        # 验证步骤数
        if data['steps_completed'] > data['total_steps']:
            logger.error("已完成步骤数不能超过总步骤数")
            return False
            
        return True


class DataSerializer:
    """数据序列化器"""
    
    @staticmethod
    def serialize_to_json(obj: Union[EmotionResult, FinalJudgment, AnalysisWorkflow], 
                         filepath: str) -> bool:
        """序列化对象到JSON文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(obj.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"序列化失败: {e}")
            return False
            
    @staticmethod
    def deserialize_from_json(filepath: str, 
                            obj_type: type) -> Optional[Union[EmotionResult, FinalJudgment, AnalysisWorkflow]]:
        """从JSON文件反序列化对象"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return obj_type.from_dict(data)
        except Exception as e:
            logger.error(f"反序列化失败: {e}")
            return None
