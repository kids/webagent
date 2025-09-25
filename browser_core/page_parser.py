from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse

class PageParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_html(self, html_content):
        """解析HTML内容并返回BeautifulSoup对象"""
        try:
            return BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            self.logger.error(f"HTML解析失败: {str(e)}")
            return None
    
    def extract_text(self, html_content, selector=None):
        """从HTML中提取文本内容，可指定选择器"""
        soup = self.parse_html(html_content)
        if not soup:
            return ""
            
        try:
            if selector:
                # 尝试使用CSS选择器
                elements = soup.select(selector)
                if elements:
                    return "\n\n".join([element.get_text(strip=True) for element in elements])
                else:
                    self.logger.warning(f"没有找到匹配选择器{selector}的元素")
                    return ""
            else:
                # 提取整个页面文本
                return soup.get_text(strip=True)
        except Exception as e:
            self.logger.error(f"文本提取失败: {str(e)}")
            return ""
    
    def extract_links(self, html_content, base_url=None):
        """从HTML中提取所有链接"""
        soup = self.parse_html(html_content)
        if not soup:
            return []
            
        try:
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # 处理相对路径
                if base_url:
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                links.append({
                    'text': a_tag.get_text(strip=True),
                    'url': full_url,
                    'original_href': href
                })
            self.logger.info(f"提取到{len(links)}个链接")
            return links
        except Exception as e:
            self.logger.error(f"链接提取失败: {str(e)}")
            return []
    
    def find_elements_by_selector(self, html_content, selector):
        """根据CSS选择器查找元素并返回其文本内容"""
        soup = self.parse_html(html_content)
        if not soup:
            return []
            
        try:
            elements = soup.select(selector)
            result = []
            for element in elements:
                result.append({
                    'text': element.get_text(strip=True),
                    'html': str(element),
                    'tag': element.name
                })
            self.logger.info(f"找到{len(result)}个匹配选择器{selector}的元素")
            return result
        except Exception as e:
            self.logger.error(f"查找选择器{selector}的元素失败: {str(e)}")
            return []
    
    def extract_metadata(self, html_content):
        """提取页面元数据，如标题、描述等"""
        soup = self.parse_html(html_content)
        if not soup:
            return {}
            
        try:
            metadata = {}
            
            # 页面标题
            title_tag = soup.title
            if title_tag:
                metadata['title'] = title_tag.get_text(strip=True)
            
            # 元描述
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and 'content' in meta_desc.attrs:
                metadata['description'] = meta_desc['content']
            
            # 其他元标签
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                if 'name' in tag.attrs and 'content' in tag.attrs:
                    metadata[f"meta_{tag['name'].lower()}"] = tag['content']
            
            self.logger.info("页面元数据提取完成")
            return metadata
        except Exception as e:
            self.logger.error(f"元数据提取失败: {str(e)}")
            return {}
