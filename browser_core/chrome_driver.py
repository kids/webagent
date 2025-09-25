from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from config.settings import Settings

class ChromeDriver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = Settings()
        self.driver = self._initialize_driver()
        self.wait = WebDriverWait(self.driver, self.settings.WEBDRIVER_WAIT_TIMEOUT)
        
    def _initialize_driver(self):
        """初始化Chrome浏览器驱动"""
        chrome_options = Options()
        
        # 配置选项
        if self.settings.HEADLESS_MODE:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.settings.USER_AGENT}")
        
        # 添加扩展或其他配置
        if self.settings.CHROME_EXTENSIONS:
            for ext in self.settings.CHROME_EXTENSIONS:
                chrome_options.add_extension(ext)
        
        # 初始化驱动
        try:
            if self.settings.CHROME_DRIVER_PATH:
                service = Service(self.settings.CHROME_DRIVER_PATH)
            else:
                # 自动管理驱动版本
                service = Service(ChromeDriverManager().install())
                
            driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Chrome驱动初始化成功")
            return driver
        except Exception as e:
            self.logger.error(f"Chrome驱动初始化失败: {str(e)}")
            raise
    
    def navigate(self, url):
        """导航到指定URL"""
        try:
            self.driver.get(url)
            self.logger.info(f"导航到URL: {url}")
            # 等待页面加载完成
            time.sleep(self.settings.PAGE_LOAD_DELAY)
            return True
        except Exception as e:
            self.logger.error(f"导航到{url}失败: {str(e)}")
            return False
    
    def go_back(self):
        """后退到上一页"""
        try:
            self.driver.back()
            self.logger.info("后退到上一页")
            time.sleep(self.settings.PAGE_LOAD_DELAY)
            return True
        except Exception as e:
            self.logger.error(f"后退操作失败: {str(e)}")
            return False
    
    def go_forward(self):
        """前进到下一页"""
        try:
            self.driver.forward()
            self.logger.info("前进到下一页")
            time.sleep(self.settings.PAGE_LOAD_DELAY)
            return True
        except Exception as e:
            self.logger.error(f"前进操作失败: {str(e)}")
            return False
    
    def click_element(self, selector, by=By.CSS_SELECTOR):
        """点击指定元素"""
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, selector)))
            element.click()
            self.logger.info(f"点击元素: {selector}")
            time.sleep(self.settings.ACTION_DELAY)
            return True
        except TimeoutException:
            self.logger.warning(f"元素{selector}超时未可点击")
            return False
        except NoSuchElementException:
            self.logger.warning(f"未找到元素{selector}")
            return False
        except Exception as e:
            self.logger.error(f"点击元素{selector}失败: {str(e)}")
            return False
    
    def type_text(self, selector, text, by=By.CSS_SELECTOR):
        """在指定元素中输入文本"""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            element.clear()
            element.send_keys(text)
            self.logger.info(f"在元素{selector}中输入文本: {text}")
            time.sleep(self.settings.ACTION_DELAY)
            return True
        except TimeoutException:
            self.logger.warning(f"元素{selector}超时未出现")
            return False
        except NoSuchElementException:
            self.logger.warning(f"未找到元素{selector}")
            return False
        except Exception as e:
            self.logger.error(f"在元素{selector}中输入文本失败: {str(e)}")
            return False
    
    def scroll(self, direction="down", pixels=None):
        """滚动页面"""
        try:
            if direction == "down":
                if pixels:
                    self.driver.execute_script(f"window.scrollBy(0, {pixels});")
                else:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.logger.info(f"向下滚动页面{pixels or '到底部'}像素")
            elif direction == "up":
                if pixels:
                    self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
                else:
                    self.driver.execute_script("window.scrollTo(0, 0);")
                self.logger.info(f"向上滚动页面{pixels or '到顶部'}像素")
            
            time.sleep(self.settings.ACTION_DELAY)
            return True
        except Exception as e:
            self.logger.error(f"页面滚动失败: {str(e)}")
            return False
    
    def get_page_source(self):
        """获取当前页面的HTML源码"""
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"获取页面源码失败: {str(e)}")
            return None
    
    def get_current_url(self):
        """获取当前页面URL"""
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"获取当前URL失败: {str(e)}")
            return None
    
    def take_screenshot(self, file_path):
        """截取当前页面并保存"""
        try:
            result = self.driver.save_screenshot(file_path)
            if result:
                self.logger.info(f"截图已保存至: {file_path}")
            else:
                self.logger.warning("截图保存失败")
            return result
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
            return False
    
    def find_elements(self, selector, by=By.CSS_SELECTOR):
        """查找符合选择器的所有元素"""
        try:
            elements = self.driver.find_elements(by, selector)
            self.logger.info(f"找到{len(elements)}个匹配{selector}的元素")
            return elements
        except NoSuchElementException:
            self.logger.warning(f"未找到匹配{selector}的元素")
            return []
        except Exception as e:
            self.logger.error(f"查找元素{selector}失败: {str(e)}")
            return []
    
    def quit(self):
        """关闭浏览器"""
        try:
            self.driver.quit()
            self.logger.info("浏览器已关闭")
        except Exception as e:
            self.logger.error(f"关闭浏览器失败: {str(e)}")
