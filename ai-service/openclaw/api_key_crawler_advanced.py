"""高级API密钥爬虫 - 增强版Selenium自动化"""

import time
import random
import json
import re
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# 可选导入selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    webdriver = None

import requests


class PlatformType(Enum):
    """平台类型"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    TOGETHER = "together"
    REPLICATE = "replicate"


@dataclass
class PlatformConfig:
    """平台配置"""
    name: str
    register_url: str
    api_url: str
    login_url: str
    free_tier: bool
    test_endpoint: str
    email_verification_required: bool = True
    phone_verification_required: bool = False
    captcha_required: bool = False


class AdvancedAPIKeyCrawler:
    """高级API密钥爬虫 - 增强功能"""

    def __init__(self, headless: bool = True, proxy: str = None):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
            proxy: 代理服务器地址，例如 "http://127.0.0.1:8080"
        """
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        self.wait = None
        self.api_keys = {}
        self.action_chains = None

        # 平台配置
        self.platforms = {
            PlatformType.DEEPSEEK: PlatformConfig(
                name="DeepSeek",
                register_url="https://platform.deepseek.com/signup",
                api_url="https://platform.deepseek.com/api-keys",
                login_url="https://platform.deepseek.com/login",
                free_tier=True,
                test_endpoint="https://api.deepseek.com/v1/models",
                email_verification_required=True
            ),
            PlatformType.OPENAI: PlatformConfig(
                name="OpenAI",
                register_url="https://auth.openai.com/signup",
                api_url="https://platform.openai.com/api-keys",
                login_url="https://platform.openai.com/login",
                free_tier=False,
                test_endpoint="https://api.openai.com/v1/models",
                email_verification_required=True,
                phone_verification_required=True
            ),
            PlatformType.ANTHROPIC: PlatformConfig(
                name="Anthropic (Claude)",
                register_url="https://console.anthropic.com/signup",
                api_url="https://console.anthropic.com/settings/keys",
                login_url="https://console.anthropic.com/login",
                free_tier=True,
                test_endpoint="https://api.anthropic.com/v1/messages",
                email_verification_required=True
            ),
            PlatformType.GROQ: PlatformConfig(
                name="Groq",
                register_url="https://console.groq.com/signup",
                api_url="https://console.groq.com/keys",
                login_url="https://console.groq.com/login",
                free_tier=True,
                test_endpoint="https://api.groq.com/openai/v1/models",
                email_verification_required=True
            ),
            PlatformType.COHERE: PlatformConfig(
                name="Cohere",
                register_url="https://dashboard.cohere.ai/register",
                api_url="https://dashboard.cohere.ai/api-keys",
                login_url="https://dashboard.cohere.ai/login",
                free_tier=True,
                test_endpoint="https://api.cohere.com/v1/models",
                email_verification_required=True
            ),
            PlatformType.HUGGINGFACE: PlatformConfig(
                name="Hugging Face",
                register_url="https://huggingface.co/join",
                api_url="https://huggingface.co/settings/tokens",
                login_url="https://huggingface.co/login",
                free_tier=True,
                test_endpoint="https://api-inference.huggingface.co/models",
                email_verification_required=True
            ),
            PlatformType.TOGETHER: PlatformConfig(
                name="Together AI",
                register_url="https://api.together.xyz/signup",
                api_url="https://api.together.xyz/settings/api-keys",
                login_url="https://api.together.xyz/login",
                free_tier=True,
                test_endpoint="https://api.together.xyz/v1/models",
                email_verification_required=True
            ),
            PlatformType.REPLICATE: PlatformConfig(
                name="Replicate",
                register_url="https://replicate.com/signin",
                api_url="https://replicate.com/account/api-tokens",
                login_url="https://replicate.com/signin",
                free_tier=True,
                test_endpoint="https://api.replicate.com/v1/models",
                email_verification_required=True
            )
        }

        # 用户代理列表
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        ]

    def _get_random_user_agent(self) -> str:
        """获取随机用户代理"""
        return random.choice(self.user_agents)

    def _init_driver(self) -> bool:
        """初始化浏览器驱动 - 增强版"""
        if not SELENIUM_AVAILABLE:
            print("Selenium未安装，无法使用浏览器自动化功能")
            return False

        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        # 基本配置
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')

        # 设置用户代理
        chrome_options.add_argument(f'user-agent={self._get_random_user_agent()}')

        # 代理配置
        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')

        # 禁用自动化检测
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 禁用图片和CSS以提高速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 执行CDP命令隐藏webdriver属性
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            self.wait = WebDriverWait(self.driver, 20)
            self.action_chains = ActionChains(self.driver)

            return True
        except Exception as e:
            print(f"初始化浏览器失败: {e}")
            return False

    def _random_sleep(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机等待"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def _human_type(self, element, text: str, min_delay: float = 0.05, max_delay: float = 0.15):
        """模拟人类输入"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))

    def _human_click(self, element):
        """模拟人类点击"""
        # 移动到元素
        self.action_chains.move_to_element(element)
        self._random_sleep(0.1, 0.3)

        # 随机偏移点击
        action = ActionChains(self.driver)
        action.move_to_element_with_offset(
            element,
            random.randint(-5, 5),
            random.randint(-5, 5)
        )
        action.click()
        action.perform()

    def _scroll_to_element(self, element):
        """滚动到元素"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        self._random_sleep(0.5, 1.0)

    def _safe_find_element(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """安全查找元素"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None

    def _safe_find_elements(self, by: By, value: str, timeout: int = 10) -> List[Any]:
        """安全查找多个元素"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except TimeoutException:
            return []

    def _wait_for_page_load(self, timeout: int = 30):
        """等待页面加载完成"""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def _close_driver(self):
        """关闭浏览器驱动"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"关闭浏览器失败: {e}")
            finally:
                self.driver = None
                self.wait = None
                self.action_chains = None

    def register_account_advanced(
        self,
        platform: PlatformType,
        email: str,
        password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        高级账户注册

        Args:
            platform: 平台类型
            email: 邮箱地址
            password: 密码
            **kwargs: 其他参数
                - name: 用户名
                - phone: 手机号
                - organization: 组织名称
                - callback: 回调函数，用于处理验证码等

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
            self.driver.get(platform_config.register_url)
            self._wait_for_page_load()
            self._random_sleep(2, 4)

            # 检查是否有验证码
            if platform_config.captcha_required:
                callback = kwargs.get("callback")
                if callback:
                    callback("captcha_required", {"url": self.driver.current_url})

            # 填写注册表单
            registration_result = self._fill_registration_form_advanced(
                platform,
                email,
                password,
                **kwargs
            )

            if not registration_result["success"]:
                return registration_result

            # 等待注册完成
            self._random_sleep(3, 5)

            # 检查是否需要邮箱验证
            if platform_config.email_verification_required:
                return {
                    "success": True,
                    "platform": platform.value,
                    "email": email,
                    "message": "注册表单提交成功，请查收验证邮件并完成验证",
                    "verification_required": True,
                    "next_step": "email_verification"
                }

            return {
                "success": True,
                "platform": platform.value,
                "email": email,
                "message": "注册成功"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"注册失败: {str(e)}"
            }
        finally:
            self._close_driver()

    def _fill_registration_form_advanced(
        self,
        platform: PlatformType,
        email: str,
        password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """高级注册表单填写"""
        try:
            # 查找邮箱输入框 - 尝试多种选择器
            email_selectors = [
                (By.NAME, "email"),
                (By.ID, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.XPATH, "//input[@placeholder='Email' or @placeholder='邮箱' or contains(@placeholder, 'email')]"),
                (By.XPATH, "//input[contains(@name, 'email') or contains(@id, 'email')]")
            ]

            email_input = None
            for by, value in email_selectors:
                email_input = self._safe_find_element(by, value, timeout=5)
                if email_input:
                    break

            if not email_input:
                return {
                    "success": False,
                    "error": "无法找到邮箱输入框"
                }

            self._scroll_to_element(email_input)
            self._human_type(email_input, email)
            self._random_sleep(0.5, 1.0)

            # 查找密码输入框
            password_selectors = [
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@placeholder='Password' or @placeholder='密码' or contains(@placeholder, 'password')]")
            ]

            password_input = None
            for by, value in password_selectors:
                password_input = self._safe_find_element(by, value, timeout=5)
                if password_input:
                    break

            if password_input:
                self._scroll_to_element(password_input)
                self._human_type(password_input, password)
                self._random_sleep(0.5, 1.0)

            # 查找确认密码输入框
            confirm_selectors = [
                (By.NAME, "confirm_password"),
                (By.NAME, "password_confirmation"),
                (By.ID, "confirm_password"),
                (By.XPATH, "//input[@placeholder='Confirm Password' or @placeholder='确认密码']")
            ]

            for by, value in confirm_selectors:
                confirm_input = self._safe_find_element(by, value, timeout=3)
                if confirm_input:
                    self._scroll_to_element(confirm_input)
                    self._human_type(confirm_input, password)
                    self._random_sleep(0.5, 1.0)
                    break

            # 查找用户名输入框（如果有）
            name = kwargs.get("name", "")
            if name:
                name_selectors = [
                    (By.NAME, "name"),
                    (By.NAME, "username"),
                    (By.ID, "name"),
                    (By.ID, "username"),
                    (By.XPATH, "//input[@placeholder='Name' or @placeholder='用户名']")
                ]

                for by, value in name_selectors:
                    name_input = self._safe_find_element(by, value, timeout=3)
                    if name_input:
                        self._scroll_to_element(name_input)
                        self._human_type(name_input, name)
                        self._random_sleep(0.5, 1.0)
                        break

            # 查找并点击注册按钮
            button_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), '注册') or contains(text(), 'Sign up') or contains(text(), 'Create account') or contains(text(), 'Submit')]"),
                (By.CSS_SELECTOR, "button.btn-primary"),
                (By.CSS_SELECTOR, "button[type='submit']")
            ]

            register_button = None
            for by, value in button_selectors:
                register_button = self._safe_find_element(by, value, timeout=5)
                if register_button:
                    break

            if register_button:
                self._scroll_to_element(register_button)
                self._human_click(register_button)
            else:
                return {
                    "success": False,
                    "error": "无法找到注册按钮"
                }

            return {
                "success": True,
                "message": "表单填写完成"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"填写表单失败: {str(e)}"
            }

    def batch_register(
        self,
        platforms: List[PlatformType],
        email: str,
        password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量注册多个平台

        Args:
            platforms: 平台列表
            email: 邮箱地址
            password: 密码
            **kwargs: 其他参数

        Returns:
            批量注册结果
        """
        results = {
            "success": True,
            "email": email,
            "platforms": {},
            "timestamp": datetime.now().isoformat()
        }

        for platform in platforms:
            print(f"正在注册 {platform.value}...")
            result = self.register_account_advanced(platform, email, password, **kwargs)
            results["platforms"][platform.value] = result

            # 随机延迟，避免被检测
            self._random_sleep(5, 10)

        # 统计结果
        success_count = sum(1 for r in results["platforms"].values() if r.get("success"))
        results["summary"] = {
            "total": len(platforms),
            "success": success_count,
            "failed": len(platforms) - success_count
        }

        return results

    def verify_email(self, platform: PlatformType, verification_code: str) -> Dict[str, Any]:
        """
        验证邮箱

        Args:
            platform: 平台类型
            verification_code: 验证码

        Returns:
            验证结果
        """
        # 这里可以实现自动邮箱验证逻辑
        # 需要接入邮箱API（如IMAP/POP3）
        return {
            "success": False,
            "error": "自动邮箱验证功能需要接入邮箱API",
            "message": "请手动完成邮箱验证"
        }

    def auto_verify_email_with_api(
        self,
        platform: PlatformType,
        email: str,
        email_password: str,
        email_server: str = "imap.126.com",
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        使用邮箱API自动验证

        Args:
            platform: 平台类型
            email: 邮箱地址
            email_password: 邮箱密码
            email_server: 邮箱服务器
            timeout: 超时时间（秒）

        Returns:
            验证结果
        """
        try:
            import imaplib
            import email
            from email.header import decode_header

            # 连接邮箱服务器
            mail = imaplib.IMAP4_SSL(email_server)
            mail.login(email, email_password)
            mail.select("inbox")

            # 等待验证邮件
            start_time = time.time()
            while time.time() - start_time < timeout:
                # 搜索未读邮件
                _, messages = mail.search(None, "UNSEEN")
                message_ids = messages[0].split()

                for msg_id in message_ids:
                    _, msg_data = mail.fetch(msg_id, "(RFC822)")
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)

                    # 检查是否是验证邮件
                    subject = decode_header(email_message["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()

                    # 根据平台检查邮件主题
                    platform_config = self.platforms[platform]
                    if platform_config.name.lower() in subject.lower():
                        # 提取验证码或验证链接
                        body = self._extract_email_body(email_message)

                        # 查找验证码
                        code_match = re.search(r'\b\d{6}\b', body)
                        if code_match:
                            verification_code = code_match.group()

                            # 标记邮件为已读
                            mail.store(msg_id, "+FLAGS", "\\Seen")
                            mail.logout()

                            return {
                                "success": True,
                                "verification_code": verification_code,
                                "message": "成功获取验证码"
                            }

                # 等待后重试
                time.sleep(10)

            mail.logout()
            return {
                "success": False,
                "error": "超时：未收到验证邮件"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"邮箱验证失败: {str(e)}"
            }

    def _extract_email_body(self, email_message) -> str:
        """提取邮件正文"""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" or content_type == "text/html":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                pass
        return body


class APIKeyCrawlerPool:
    """API密钥爬虫池 - 管理多个爬虫实例"""

    def __init__(self, max_workers: int = 3):
        """
        初始化爬虫池

        Args:
            max_workers: 最大并发数
        """
        self.max_workers = max_workers
        self.crawlers = []
        self.results = []

    def create_crawler(self, headless: bool = True, proxy: str = None) -> AdvancedAPIKeyCrawler:
        """创建爬虫实例"""
        crawler = AdvancedAPIKeyCrawler(headless=headless, proxy=proxy)
        self.crawlers.append(crawler)
        return crawler

    def parallel_register(
        self,
        tasks: List[Dict[str, Any]],
        callback: Callable = None
    ) -> List[Dict[str, Any]]:
        """
        并行注册多个账户

        Args:
            tasks: 任务列表，每个任务包含 platform, email, password 等
            callback: 回调函数

        Returns:
            注册结果列表
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}

            for task in tasks:
                crawler = self.create_crawler()
                future = executor.submit(
                    crawler.register_account_advanced,
                    task["platform"],
                    task["email"],
                    task["password"],
                    **task.get("kwargs", {})
                )
                future_to_task[future] = task

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append({
                        "task": task,
                        "result": result
                    })

                    if callback:
                        callback(task, result)

                except Exception as e:
                    results.append({
                        "task": task,
                        "result": {
                            "success": False,
                            "error": str(e)
                        }
                    })

        return results


# 便捷函数
def register_single_platform(
    platform: str,
    email: str,
    password: str,
    headless: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    注册单个平台

    Args:
        platform: 平台名称
        email: 邮箱地址
        password: 密码
        headless: 是否使用无头模式
        **kwargs: 其他参数

    Returns:
        注册结果
    """
    try:
        platform_type = PlatformType(platform.lower())
    except ValueError:
        return {
            "success": False,
            "error": f"不支持的平台: {platform}"
        }

    crawler = AdvancedAPIKeyCrawler(headless=headless)
    return crawler.register_account_advanced(platform_type, email, password, **kwargs)


def batch_register_platforms(
    platforms: List[str],
    email: str,
    password: str,
    headless: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    批量注册多个平台

    Args:
        platforms: 平台名称列表
        email: 邮箱地址
        password: 密码
        headless: 是否使用无头模式
        **kwargs: 其他参数

    Returns:
        批量注册结果
    """
    platform_types = []
    for platform in platforms:
        try:
            platform_types.append(PlatformType(platform.lower()))
        except ValueError:
            print(f"警告: 不支持的平台 {platform}，已跳过")

    if not platform_types:
        return {
            "success": False,
            "error": "没有有效的平台"
        }

    crawler = AdvancedAPIKeyCrawler(headless=headless)
    return crawler.batch_register(platform_types, email, password, **kwargs)


def parallel_register(
    tasks: List[Dict[str, Any]],
    max_workers: int = 3,
    callback: Callable = None
) -> List[Dict[str, Any]]:
    """
    并行注册

    Args:
        tasks: 任务列表
        max_workers: 最大并发数
        callback: 回调函数

    Returns:
        注册结果列表
    """
    pool = APIKeyCrawlerPool(max_workers=max_workers)
    return pool.parallel_register(tasks, callback)
