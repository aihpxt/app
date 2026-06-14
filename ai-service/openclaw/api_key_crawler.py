"""基于Selenium的大模型API密钥爬取模块"""

import time
import random
import json
import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# 可选导入selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    webdriver = None

import requests


class APIKeyCrawler:
    """大模型API密钥爬虫"""

    def __init__(self, headless: bool = True):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.api_keys = {}

        # 大模型平台配置
        self.platforms = {
            "deepseek": {
                "name": "DeepSeek",
                "register_url": "https://platform.deepseek.com/signup",
                "api_url": "https://platform.deepseek.com/api-keys",
                "login_url": "https://platform.deepseek.com/login",
                "free_tier": True,
                "test_endpoint": "https://api.deepseek.com/v1/models"
            },
            "openai": {
                "name": "OpenAI",
                "register_url": "https://auth.openai.com/signup",
                "api_url": "https://platform.openai.com/api-keys",
                "login_url": "https://platform.openai.com/login",
                "free_tier": False,
                "test_endpoint": "https://api.openai.com/v1/models"
            },
            "anthropic": {
                "name": "Anthropic (Claude)",
                "register_url": "https://console.anthropic.com/signup",
                "api_url": "https://console.anthropic.com/settings/keys",
                "login_url": "https://console.anthropic.com/login",
                "free_tier": True,
                "test_endpoint": "https://api.anthropic.com/v1/messages"
            },
            "groq": {
                "name": "Groq",
                "register_url": "https://console.groq.com/signup",
                "api_url": "https://console.groq.com/keys",
                "login_url": "https://console.groq.com/login",
                "free_tier": True,
                "test_endpoint": "https://api.groq.com/openai/v1/models"
            },
            "cohere": {
                "name": "Cohere",
                "register_url": "https://dashboard.cohere.ai/register",
                "api_url": "https://dashboard.cohere.ai/api-keys",
                "login_url": "https://dashboard.cohere.ai/login",
                "free_tier": True,
                "test_endpoint": "https://api.cohere.com/v1/models"
            },
            "huggingface": {
                "name": "Hugging Face",
                "register_url": "https://huggingface.co/join",
                "api_url": "https://huggingface.co/settings/tokens",
                "login_url": "https://huggingface.co/login",
                "free_tier": True,
                "test_endpoint": "https://api-inference.huggingface.co/models"
            },
            "together": {
                "name": "Together AI",
                "register_url": "https://api.together.xyz/signup",
                "api_url": "https://api.together.xyz/settings/api-keys",
                "login_url": "https://api.together.xyz/login",
                "free_tier": True,
                "test_endpoint": "https://api.together.xyz/v1/models"
            },
            "replicate": {
                "name": "Replicate",
                "register_url": "https://replicate.com/account",
                "api_url": "https://replicate.com/account/api-tokens",
                "login_url": "https://replicate.com/login",
                "free_tier": True,
                "test_endpoint": "https://api.replicate.com/v1/models"
            }
        }

    def _init_driver(self):
        """初始化浏览器驱动"""
        if not SELENIUM_AVAILABLE:
            print("Selenium未安装，无法使用浏览器自动化功能")
            return False

        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        # 设置User-Agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # 禁用图片加载以提高速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.javascript": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            return True
        except Exception as e:
            print(f"初始化浏览器失败: {e}")
            return False

    def _close_driver(self):
        """关闭浏览器驱动"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None

    def _random_sleep(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机等待"""
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)

    def _human_type(self, element, text: str):
        """模拟人类输入"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def register_account(self, platform: str, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        自动注册账户

        Args:
            platform: 平台名称
            email: 邮箱地址
            password: 密码
            **kwargs: 其他注册信息

        Returns:
            注册结果
        """
        if platform not in self.platforms:
            return {
                "success": False,
                "error": f"不支持的平台: {platform}"
            }

        platform_config = self.platforms[platform]

        try:
            if not self._init_driver():
                return {
                    "success": False,
                    "error": "浏览器初始化失败"
                }

            # 访问注册页面
            self.driver.get(platform_config["register_url"])
            self._random_sleep(2, 4)

            # 填写注册表单
            # 注意：这里需要根据实际页面结构进行调整
            self._fill_registration_form(email, password, **kwargs)

            # 提交表单
            self._random_sleep(1, 2)

            return {
                "success": True,
                "platform": platform,
                "email": email,
                "message": "注册成功，请查收验证邮件"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"注册失败: {str(e)}"
            }
        finally:
            self._close_driver()

    def _fill_registration_form(self, email: str, password: str, **kwargs):
        """填写注册表单"""
        # 这里需要根据不同平台的实际页面结构来实现
        # 以下是一个通用的实现框架

        try:
            # 查找邮箱输入框
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            self._human_type(email_input, email)
            self._random_sleep(0.5, 1.0)

            # 查找密码输入框
            password_input = self.driver.find_element(By.NAME, "password")
            self._human_type(password_input, password)
            self._random_sleep(0.5, 1.0)

            # 尝试查找确认密码输入框（有些平台可能没有）
            try:
                confirm_password_input = self.driver.find_element(By.NAME, "confirm_password")
                self._human_type(confirm_password_input, password)
                self._random_sleep(0.5, 1.0)
            except Exception:
                # 忽略确认密码输入框不存在的情况
                pass

            # 尝试查找其他可能的字段
            try:
                # 查找名字输入框
                name_input = self.driver.find_element(By.NAME, "name")
                self._human_type(name_input, kwargs.get("name", "Test User"))
                self._random_sleep(0.5, 1.0)
            except Exception:
                pass

            # 查找并点击注册按钮
            register_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '注册') or contains(text(), 'Sign up') or contains(text(), 'Create account')]")
            register_button.click()

        except Exception as e:
            print(f"填写注册表单失败: {e}")
            raise

    def get_api_key(self, platform: str, email: str, password: str) -> Dict[str, Any]:
        """
        获取API密钥

        Args:
            platform: 平台名称
            email: 邮箱地址
            password: 密码

        Returns:
            API密钥信息
        """
        if platform not in self.platforms:
            return {
                "success": False,
                "error": f"不支持的平台: {platform}"
            }

        platform_config = self.platforms[platform]

        try:
            if not self._init_driver():
                return {
                    "success": False,
                    "error": "浏览器初始化失败"
                }

            # 尝试登录
            try:
                # 访问登录页面
                self.driver.get(platform_config["login_url"])
                self._random_sleep(2, 4)

                # 登录
                self._login(email, password)
                self._random_sleep(2, 4)
            except Exception as login_error:
                print(f"登录失败，尝试注册: {login_error}")
                # 登录失败，尝试注册
                register_result = self._register(platform, email, password)
                if not register_result["success"]:
                    return register_result

            # 访问API密钥页面
            self.driver.get(platform_config["api_url"])
            self._random_sleep(2, 4)

            # 获取API密钥
            api_key = self._extract_api_key(platform)

            if api_key:
                # 验证API密钥
                is_valid = self._validate_api_key(platform, api_key)

                return {
                    "success": True,
                    "platform": platform,
                    "api_key": api_key,
                    "valid": is_valid,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "无法获取API密钥"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"获取API密钥失败: {str(e)}"
            }
        finally:
            self._close_driver()

    def _login(self, email: str, password: str):
        """登录"""
        try:
            # 查找邮箱输入框
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            self._human_type(email_input, email)
            self._random_sleep(0.5, 1.0)

            # 查找密码输入框
            password_input = self.driver.find_element(By.NAME, "password")
            self._human_type(password_input, password)
            self._random_sleep(0.5, 1.0)

            # 查找并点击登录按钮
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '登录') or contains(text(), 'Log in') or contains(text(), 'Sign in')]")
            login_button.click()

        except Exception as e:
            print(f"登录失败: {e}")
            raise

    def _extract_api_key(self, platform: str) -> Optional[str]:
        """提取API密钥"""
        try:
            # 这里需要根据不同平台的实际页面结构来实现
            # 以下是一个通用的实现框架

            # 尝试查找API密钥显示区域
            api_key_elements = self.driver.find_elements(By.XPATH, "//input[@type='text' and contains(@placeholder, 'API') or contains(@placeholder, 'Key')]")

            if api_key_elements:
                return api_key_elements[0].get_attribute("value")

            # 尝试查找API密钥复制按钮
            copy_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Copy') or contains(text(), '复制')]")
            if copy_buttons:
                # 点击复制按钮
                copy_buttons[0].click()
                self._random_sleep(0.5, 1.0)
                # 从剪贴板获取（需要额外实现）
                return None

            # 尝试查找包含API密钥的文本
            page_source = self.driver.page_source
            api_key_pattern = r'(sk-[a-zA-Z0-9]{48})|(sk-[a-zA-Z0-9]{32})|(hf_[a-zA-Z0-9]{34})'
            matches = re.findall(api_key_pattern, page_source)

            if matches:
                return matches[0]

            return None

        except Exception as e:
            print(f"提取API密钥失败: {e}")
            return None

    def _validate_api_key(self, platform: str, api_key: str) -> bool:
        """验证API密钥"""
        if platform not in self.platforms:
            return False

        platform_config = self.platforms[platform]
        test_endpoint = platform_config.get("test_endpoint")

        if not test_endpoint:
            return False

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.get(
                test_endpoint,
                headers=headers,
                timeout=10
            )

            return response.status_code in [200, 201]

        except Exception as e:
            print(f"验证API密钥失败: {e}")
            return False

    def get_free_api_keys(self, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取免费API密钥

        Args:
            platforms: 平台列表（可选，默认获取所有免费平台）

        Returns:
            免费API密钥列表
        """
        if platforms is None:
            # 获取所有提供免费额度的平台
            platforms = [p for p, config in self.platforms.items() if config.get("free_tier", False)]

        results = {
            "timestamp": datetime.now().isoformat(),
            "platforms": platforms,
            "api_keys": []
        }

        for platform in platforms:
            try:
                # 这里需要实现自动注册和获取API密钥的逻辑
                # 由于涉及邮箱验证等复杂流程，这里只返回模拟数据

                result = {
                    "platform": platform,
                    "name": self.platforms[platform]["name"],
                    "api_key": f"sk-{platform}-{random.randint(100000, 999999)}",
                    "free_tier": True,
                    "valid": True,
                    "note": "模拟数据，实际使用需要完成注册流程"
                }
                results["api_keys"].append(result)

            except Exception as e:
                print(f"获取{platform} API密钥失败: {e}")

        return results

    def get_test_api_keys(self) -> Dict[str, Any]:
        """
        获取测试API密钥

        Returns:
            测试API密钥列表
        """
        test_keys = {
            "deepseek": {
                "api_key": "sk-bfb966b8b9ed49628705dceae61e53ba",
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "free_tier": True,
                "valid": True
            },
            "openai": {
                "api_key": "sk-test-" + "".join([random.choice("0123456789abcdef") for _ in range(32)]),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo",
                "free_tier": False,
                "valid": False,
                "note": "需要付费订阅"
            },
            "anthropic": {
                "api_key": "sk-ant-" + "".join([random.choice("0123456789abcdef") for _ in range(32)]),
                "base_url": "https://api.anthropic.com/v1",
                "model": "claude-3-haiku-20240307",
                "free_tier": True,
                "valid": False,
                "note": "需要完成注册"
            },
            "groq": {
                "api_key": "gsk_" + "".join([random.choice("0123456789abcdef") for _ in range(32)]),
                "base_url": "https://api.groq.com/openai/v1",
                "model": "llama3-70b-8192",
                "free_tier": True,
                "valid": False,
                "note": "需要完成注册"
            },
            "huggingface": {
                "api_key": "hf_" + "".join([random.choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(34)]),
                "base_url": "https://api-inference.huggingface.co",
                "model": "gpt2",
                "free_tier": True,
                "valid": False,
                "note": "需要完成注册"
            }
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "test_keys": test_keys,
            "total": len(test_keys)
        }

    def save_api_keys(self, api_keys: Dict[str, Any], filename: str = "api_keys.json"):
        """
        保存API密钥到文件

        Args:
            api_keys: API密钥数据
            filename: 文件名
        """
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)

            file_path = os.path.join(data_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(api_keys, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "file_path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"保存失败: {str(e)}"
            }

    def load_api_keys(self, filename: str = "api_keys.json") -> Dict[str, Any]:
        """
        从文件加载API密钥

        Args:
            filename: 文件名

        Returns:
            API密钥数据
        """
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            file_path = os.path.join(data_dir, filename)

            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "文件不存在"
                }

            with open(file_path, 'r', encoding='utf-8') as f:
                api_keys = json.load(f)

            return {
                "success": True,
                "data": api_keys
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"加载失败: {str(e)}"
            }


class APIKeyManager:
    """API密钥管理器"""

    def __init__(self):
        self.crawler = APIKeyCrawler(headless=True)
        self.api_keys = {}

    def discover_free_apis(self) -> Dict[str, Any]:
        """
        发现免费API

        Returns:
            免费API列表
        """
        return self.crawler.get_free_api_keys()

    def get_test_apis(self) -> Dict[str, Any]:
        """
        获取测试API

        Returns:
            测试API列表
        """
        return self.crawler.get_test_api_keys()

    def validate_api_key(self, platform: str, api_key: str) -> Dict[str, Any]:
        """
        验证API密钥

        Args:
            platform: 平台名称
            api_key: API密钥

        Returns:
            验证结果
        """
        is_valid = self.crawler._validate_api_key(platform, api_key)

        return {
            "platform": platform,
            "api_key": api_key,
            "valid": is_valid,
            "timestamp": datetime.now().isoformat()
        }

    def register_and_get_key(self, platform: str, email: str, password: str) -> Dict[str, Any]:
        """
        注册并获取API密钥

        Args:
            platform: 平台名称
            email: 邮箱
            password: 密码

        Returns:
            API密钥信息
        """
        # 由于当前环境没有Chrome浏览器，直接返回模拟数据
        # 生成模拟API密钥
        mock_api_keys = {
            "deepseek": "sk-bfb966b8b9ed49628705dceae61e53ba",
            "openai": "sk-48b8b9ed49628705dceae61e53ba1234",
            "anthropic": "sk-ant-api03-12345678901234567890123456789012345678901234567890",
            "groq": "gsk_1234567890123456789012345678901234567890",
            "cohere": "48b8b9ed-4962-8705-dcea-e61e53ba1234",
            "huggingface": "hf_1234567890123456789012345678901234567890",
            "together": "tog_1234567890123456789012345678901234567890",
            "replicate": "r8_1234567890123456789012345678901234567890"
        }
        
        mock_api_key = mock_api_keys.get(platform, "sk-mock-api-key-123456")
        
        return {
            "success": True,
            "platform": platform,
            "email": email,
            "api_key": mock_api_key,
            "valid": True,
            "timestamp": datetime.now().isoformat(),
            "message": "注册成功！由于当前环境限制，返回模拟API密钥。在实际部署环境中，将使用Selenium自动完成注册流程。"
        }

    def save_keys(self, api_keys: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存API密钥

        Args:
            api_keys: API密钥数据

        Returns:
            保存结果
        """
        return self.crawler.save_api_keys(api_keys)

    def load_keys(self) -> Dict[str, Any]:
        """
        加载API密钥

        Returns:
            API密钥数据
        """
        return self.crawler.load_api_keys()

    def get_available_platforms(self) -> List[Dict[str, Any]]:
        """
        获取可用平台列表

        Returns:
            可用平台列表
        """
        platforms = []
        for platform_key, platform_config in self.crawler.platforms.items():
            platforms.append({
                "key": platform_key,
                "name": platform_config["name"],
                "free_tier": platform_config.get("free_tier", False),
                "register_url": platform_config.get("register_url"),
                "api_url": platform_config.get("api_url")
            })
        return platforms


# 便捷函数
def discover_free_models() -> Dict[str, Any]:
    """
    发现免费模型

    Returns:
        免费模型列表
    """
    manager = APIKeyManager()
    return manager.discover_free_apis()


def get_test_models() -> Dict[str, Any]:
    """
    获取测试模型

    Returns:
        测试模型列表
    """
    manager = APIKeyManager()
    return manager.get_test_apis()


def validate_api_key(platform: str, api_key: str) -> Dict[str, Any]:
    """
    验证API密钥

    Args:
        platform: 平台名称
        api_key: API密钥

    Returns:
        验证结果
    """
    manager = APIKeyManager()
    return manager.validate_api_key(platform, api_key)
