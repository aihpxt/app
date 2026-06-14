"""多模型LLM服务 - 集成多个AI平台的API"""

import time
import random
import requests
import json
import sys
import os
from typing import Dict, Any, List, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import SYSTEM_PROMPT

# 兼容函数
def get_system_prompt(prompt_type: str = "default") -> str:
    """获取系统提示词"""
    return SYSTEM_PROMPT

# 尝试导入api_keys_config，如果不存在则使用默认配置
try:
    from api_keys_config import get_api_key_config, get_all_api_keys, get_free_tier_apis
except ImportError:
    # 提供默认配置
    def get_api_key_config(platform):
        """默认API密钥配置"""
        default_configs = {
            "deepseek": {
                "api_key": "sk-bfb966b8b9ed49628705dceae61e53ba",
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat"
            }
        }
        return default_configs.get(platform)
    
    def get_all_api_keys():
        """默认API密钥"""
        return {"deepseek": {"api_key": "sk-bfb966b8b9ed49628705dceae61e53ba"}}
    
    def get_free_tier_apis():
        """默认免费API"""
        return {"deepseek": {"api_key": "sk-bfb966b8b9ed49628705dceae61e53ba"}}

class MultiLLMService:
    """多模型LLM服务 - 支持多个AI平台"""

    def __init__(self, platform: str = "deepseek"):
        """
        初始化多模型服务

        Args:
            platform: 平台名称，支持 deepseek, openai, anthropic, groq, huggingface, cohere, together, replicate
        """
        self.platform = platform
        self.config = get_api_key_config(platform)

        if not self.config:
            raise ValueError(f"不支持的AI平台: {platform}")

        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config.get("base_url", "")
        self.model = self.config.get("model", "")
        self.email = self.config.get("email", "")
        self.max_tokens = 2048
        self.temperature = 0.7
        self.timeout = 30

        # 平台特定的配置
        self.platform_configs = {
            "deepseek": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "openai": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "anthropic": {
                "endpoint": "/messages",
                "model_key": "model",
                "message_format": "anthropic"
            },
            "groq": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "huggingface": {
                "endpoint": "/models/" + self.model,
                "model_key": "model",
                "message_format": "huggingface"
            },
            "cohere": {
                "endpoint": "/chat",
                "model_key": "model",
                "message_format": "cohere"
            },
            "together": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "replicate": {
                "endpoint": "/predictions",
                "model_key": "version",
                "message_format": "replicate"
            },
            # 国内大模型
            "qwen": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "ernie": {
                "endpoint": "",
                "model_key": "model",
                "message_format": "ernie"
            },
            "hunyuan": {
                "endpoint": "",
                "model_key": "model",
                "message_format": "hunyuan"
            },
            "chatglm": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "kimi": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "spark": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "sensechat": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            },
            "doubao": {
                "endpoint": "/chat/completions",
                "model_key": "model",
                "message_format": "openai"
            }
        }

        self.platform_config = self.platform_configs.get(platform, self.platform_configs["deepseek"])

    def _call_api(self, messages: List[Dict[str, str]], temperature: float = None, max_tokens: int = None) -> Dict[str, Any]:
        """调用API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 根据不同平台构建请求数据
            message_format = self.platform_config["message_format"]

            if message_format == "openai":
                data = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature or self.temperature,
                    "max_tokens": max_tokens or self.max_tokens
                }
            elif message_format == "anthropic":
                data = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens or self.max_tokens,
                    "temperature": temperature or self.temperature
                }
            elif message_format == "cohere":
                # Cohere格式转换
                user_message = messages[-1]["content"] if messages else ""
                data = {
                    "model": self.model,
                    "message": user_message,
                    "temperature": temperature or self.temperature,
                    "max_tokens": max_tokens or self.max_tokens
                }
            elif message_format == "ernie":
                # 百度文心一言格式
                user_message = messages[-1]["content"] if messages else ""
                data = {
                    "messages": messages
                }
            elif message_format == "hunyuan":
                # 腾讯混元格式
                data = {
                    "Model": self.model,
                    "Messages": messages,
                    "Temperature": temperature or self.temperature,
                    "MaxTokens": max_tokens or self.max_tokens
                }
            else:
                # 默认OpenAI格式
                data = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature or self.temperature,
                    "max_tokens": max_tokens or self.max_tokens
                }

            # 特殊处理百度和腾讯的请求
            if message_format == "ernie":
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
            elif message_format == "hunyuan":
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
            else:
                response = requests.post(
                    f"{self.base_url}{self.platform_config['endpoint']}",
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )

            if response.status_code == 200:
                result = response.json()

                # 解析不同平台的响应
                content = self._parse_response(result, message_format)

                return {
                    "success": True,
                    "content": content,
                    "usage": result.get("usage", {}),
                    "model": result.get("model", self.model),
                    "platform": self.platform
                }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code}",
                    "details": response.text,
                    "platform": self.platform
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "API调用超时",
                "platform": self.platform
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"API调用异常: {str(e)}",
                "platform": self.platform
            }

    def _parse_response(self, result: Dict[str, Any], message_format: str) -> str:
        """解析API响应"""
        try:
            if message_format == "openai":
                return result["choices"][0]["message"]["content"]
            elif message_format == "anthropic":
                return result["content"][0]["text"]
            elif message_format == "cohere":
                return result.get("text", "")
            elif message_format == "huggingface":
                return result[0].get("generated_text", "") if isinstance(result, list) else str(result)
            else:
                # 默认尝试OpenAI格式
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"解析响应失败: {str(e)}"

    def generate_answer(self, prompt: str, temperature: float = 0.7, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成回答"""
        # 确定提示词类型
        prompt_type = self._determine_prompt_type(prompt)
        system_prompt = get_system_prompt(prompt_type)

        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # 添加上下文信息
        if context:
            context_str = self._format_context(context)
            messages.insert(1, {"role": "system", "content": f"上下文信息：\n{context_str}"})

        # 调用API
        result = self._call_api(messages, temperature)

        if result["success"]:
            return {
                "answer": result["content"],
                "model": result["model"],
                "platform": result["platform"],
                "usage": result.get("usage", {})
            }
        else:
            return {
                "answer": f"抱歉，{result['platform']}服务暂时不可用: {result.get('error', '未知错误')}",
                "model": self.model,
                "platform": self.platform,
                "error": result.get("error", "")
            }

    def _determine_prompt_type(self, prompt: str) -> str:
        """确定提示词类型"""
        prompt_lower = prompt.lower()

        if any(keyword in prompt_lower for keyword in ["政策", "录取", "分数线", "招生"]):
            return "policy_interpretation"
        elif any(keyword in prompt_lower for keyword in ["推荐", "学校", "选择", "适合"]):
            return "school_recommendation"
        elif any(keyword in prompt_lower for keyword in ["志愿", "填报", "方案", "冲", "稳", "保"]):
            return "volunteer_planning"
        else:
            return "general_qa"

    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文信息"""
        context_parts = []

        if "student_info" in context:
            student = context["student_info"]
            context_parts.append(f"学生信息：")
            context_parts.append(f"- 总分：{student.get('total_score', '未知')}")
            context_parts.append(f"- 排名：{student.get('rank', '未知')}")
            context_parts.append(f"- 地区：{student.get('region', '未知')}")

        if "schools" in context:
            schools = context["schools"]
            context_parts.append(f"\n学校信息：")
            for school in schools[:3]:  # 只显示前3所学校
                context_parts.append(f"- {school.get('name', '未知')}：{school.get('description', '')}")

        return "\n".join(context_parts)

    def switch_platform(self, platform: str) -> bool:
        """切换到其他AI平台"""
        try:
            new_config = get_api_key_config(platform)
            if new_config:
                self.platform = platform
                self.config = new_config
                self.api_key = new_config.get("api_key", "")
                self.base_url = new_config.get("base_url", "")
                self.model = new_config.get("model", "")
                self.platform_config = self.platform_configs.get(platform, self.platform_configs["deepseek"])
                return True
            return False
        except Exception as e:
            print(f"切换平台失败: {e}")
            return False

    def get_available_platforms(self) -> List[str]:
        """获取可用的AI平台列表"""
        all_keys = get_all_api_keys()
        return list(all_keys.keys())

    def get_free_platforms(self) -> List[str]:
        """获取免费额度的平台列表"""
        free_apis = get_free_tier_apis()
        return list(free_apis.keys())


class LLMRouter:
    """LLM路由服务 - 自动选择最佳的AI平台"""

    def __init__(self):
        self.services = {}
        # 优化平台优先级，将更快的平台放在前面
        # 优先使用国内大模型，然后是国外优质模型
        self.priority_order = [
            # 国内大模型（优先使用）
            "qwen",        # 通义千问 - 阿里云
            "kimi",        # 月之暗面 - Kimi
            "hunyuan",     # 混元 - 腾讯
            "chatglm",      # 智谱 - 清华
            "ernie",       # 文心一言 - 百度
            "doubao",      # 豆包 - 字节跳动
            "spark",       # 讯飞星火 - 科大讯飞
            "sensechat",   # 商汤日日新 - 商汤
            # 国外优质模型
            "groq",        # Groq - 极快
            "deepseek",    # DeepSeek - 高性价比
            "anthropic",   # Claude - 高质量
            "openai",      # GPT - 稳定
            "together",    # Together AI
            "cohere",      # Cohere
            "huggingface", # Hugging Face
            "replicate"    # Replicate
        ]

    def get_service(self, platform: str = None) -> MultiLLMService:
        """获取LLM服务"""
        if platform and platform not in self.services:
            try:
                self.services[platform] = MultiLLMService(platform)
            except Exception as e:
                print(f"初始化{platform}服务失败: {e}")
                return None

        if platform:
            return self.services.get(platform)

        # 如果没有指定平台，尝试按优先级获取
        for p in self.priority_order:
            if p not in self.services:
                try:
                    self.services[p] = MultiLLMService(p)
                    return self.services[p]
                except Exception as e:
                    continue

        return None

    def generate_with_fallback(self, prompt: str, temperature: float = 0.7, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成回答，支持自动故障转移

        如果首选平台失败，自动尝试其他平台
        """
        for platform in self.priority_order:
            service = self.get_service(platform)
            if service:
                result = service.generate_answer(prompt, temperature, context)
                if "error" not in result or not result["error"]:
                    return result

        # 所有平台都失败
        return {
            "answer": "抱歉，所有AI服务暂时不可用，请稍后再试。",
            "model": "none",
            "platform": "none",
            "error": "所有平台都不可用"
        }


# 全局路由实例
llm_router = LLMRouter()

def get_llm_service(platform: str = "deepseek") -> MultiLLMService:
    """获取LLM服务"""
    return llm_router.get_service(platform)

def generate_answer(prompt: str, platform: str = "deepseek", temperature: float = 0.7, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """生成回答"""
    service = get_llm_service(platform)
    if service:
        return service.generate_answer(prompt, temperature, context)
    else:
        return {
            "answer": "服务初始化失败",
            "error": "无法初始化LLM服务"
        }

def generate_with_fallback(prompt: str, temperature: float = 0.7, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """生成回答，支持自动故障转移"""
    return llm_router.generate_with_fallback(prompt, temperature, context)
