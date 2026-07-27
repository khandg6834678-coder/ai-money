# Python 实用工具脚本合集 | 30+ Production-Ready Scripts

> 每个脚本都可独立运行 | 复制即用 | 零依赖或最小依赖

## 目录

1. 文件处理 (5个)
2. 数据处理 (5个)
3. 网络工具 (5个)
4. 自动化运维 (5个)
5. 文本处理 (5个)
6. API工具 (5个)

---

## 1. 文件处理

### 1.1 批量重命名文件
```python
import os
import re
from pathlib import Path

def batch_rename(directory, pattern, replacement, dry_run=True):
    """批量重命名文件，支持正则表达式"""
    path = Path(directory)
    renamed = []
    
    for file in path.iterdir():
        if file.is_file():
            new_name = re.sub(pattern, replacement, file.name)
            if new_name != file.name:
                new_path = file.parent / new_name
                if not dry_run:
                    file.rename(new_path)
                renamed.append((file.name, new_name))
    
    for old, new in renamed:
        print(f"  {old} → {new}")
    print(f"总计: {len(renamed)} 个文件{' (预览模式)' if dry_run else ' (已执行)'}")
    
    return renamed

# 使用示例
# batch_rename("./photos", r"IMG_(\d+)\.jpg", r"photo_\1.jpg", dry_run=True)
```

### 1.2 大文件分块读取
```python
def read_file_chunks(filepath, chunk_size=8192):
    """生成器：逐块读取大文件，内存友好"""
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def count_lines_fast(filepath):
    """快速计算文件行数（大文件适用）"""
    count = 0
    with open(filepath, 'rb') as f:
        for _ in f:
            count += 1
    return count
```

### 1.3 文件格式转换器
```python
import csv
import json

def csv_to_json(csv_path, json_path):
    """CSV转JSON"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 转换完成: {len(data)} 行 → {json_path}")

def json_to_csv(json_path, csv_path):
    """JSON转CSV"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        print("⚠️ 没有数据")
        return
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ 转换完成: {len(data)} 行 → {csv_path}")
```

### 1.4 重复文件查找器
```python
import hashlib
from collections import defaultdict

def find_duplicate_files(directory):
    """通过MD5哈希查找重复文件"""
    hash_map = defaultdict(list)
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                hash_map[file_hash].append(filepath)
            except (IOError, OSError):
                continue
    
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    
    for h, paths in duplicates.items():
        print(f"重复文件 (MD5: {h[:8]}...):")
        for p in paths:
            print(f"  - {p} ({os.path.getsize(p)} bytes)")
        print()
    
    return duplicates
```

### 1.5 目录同步工具
```python
import shutil

def sync_directories(source, target, delete_extras=False):
    """单向同步目录（源→目标）"""
    stats = {"copied": 0, "updated": 0, "deleted": 0, "skipped": 0}
    
    for root, dirs, files in os.walk(source):
        rel_path = os.path.relpath(root, source)
        target_dir = os.path.join(target, rel_path)
        os.makedirs(target_dir, exist_ok=True)
        
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_dir, f)
            
            if not os.path.exists(dst_file):
                shutil.copy2(src_file, dst_file)
                stats["copied"] += 1
            elif os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                shutil.copy2(src_file, dst_file)
                stats["updated"] += 1
            else:
                stats["skipped"] += 1
    
    print(f"同步完成: 新增{stats['copied']}, 更新{stats['updated']}, 跳过{stats['skipped']}")
    return stats
```

---

## 2. 数据处理

### 2.1 Excel批量处理
```python
try:
    import openpyxl
except ImportError:
    print("需要安装: pip install openpyxl")

def merge_excel_files(file_list, output_path):
    """合并多个Excel文件到同一个工作表"""
    import openpyxl
    
    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    row_idx = 1
    
    for filepath in file_list:
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
        for row in ws.iter_rows(values_only=True):
            ws_out.append(row)
            row_idx += 1
        wb.close()
    
    wb_out.save(output_path)
    print(f"✅ 合并完成: {row_idx - 1} 行 → {output_path}")
```

### 2.2 数据脱敏工具
```python
import re

def mask_sensitive_data(text):
    """对敏感信息进行脱敏处理"""
    # 手机号: 138****1234
    text = re.sub(r'(1[3-9]\d)\d{4}(\d{4})', r'\1****\2', text)
    # 邮箱: t***@domain.com
    text = re.sub(r'(\w)[^@]+(\w@\w+\.\w+)', r'\1***\2', text)
    # 身份证: 310***********1234
    text = re.sub(r'(\d{3})\d{11}(\d{4})', r'\1***********\2', text)
    return text
```

### 2.3 数据采样器
```python
import random

def reservoir_sample(iterator, k):
    """蓄水池抽样：从未知大小的流中均匀抽取k个样本"""
    reservoir = []
    for i, item in enumerate(iterator):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir
```

### 2.4 时间序列聚合
```python
from datetime import datetime, timedelta
from collections import defaultdict

def aggregate_by_interval(data, interval_minutes=60):
    """按时间间隔聚合数据"""
    buckets = defaultdict(list)
    
    for timestamp, value in data:
        dt = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp
        bucket_key = dt.replace(
            minute=dt.minute // interval_minutes * interval_minutes,
            second=0, microsecond=0
        )
        buckets[bucket_key].append(value)
    
    result = {}
    for bucket_key, values in sorted(buckets.items()):
        result[bucket_key.isoformat()] = {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }
    
    return result
```

### 2.5 数据验证框架
```python
from dataclasses import dataclass
from typing import Any, Callable, List

@dataclass
class ValidationRule:
    field: str
    rule: Callable[[Any], bool]
    message: str

def validate_data(data_list, rules):
    """对数据列表进行批量验证"""
    errors = []
    
    for i, record in enumerate(data_list):
        for rule in rules:
            value = record.get(rule.field)
            if not rule.rule(value):
                errors.append({
                    "row": i,
                    "field": rule.field,
                    "value": value,
                    "error": rule.message
                })
    
    if errors:
        print(f"❌ 验证失败: {len(errors)} 个错误")
        for e in errors[:10]:  # 只显示前10个
            print(f"  行{e['row']}, 字段'{e['field']}': {e['error']} (值: {e['value']})")
    else:
        print(f"✅ 全部通过: {len(data_list)} 条记录验证成功")
    
    return errors
```

---

## 3. 网络工具

### 3.1 网站可用性监控
```python
import urllib.request
import time
from datetime import datetime

def monitor_website(url, interval_seconds=60, max_checks=None):
    """监控网站可用性"""
    checks = 0
    history = []
    
    while max_checks is None or checks < max_checks:
        checks += 1
        start = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MonitorBot/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            elapsed = time.time() - start
            status = "UP"
            history.append({
                "time": datetime.now().isoformat(),
                "status": status,
                "code": resp.status,
                "latency_ms": round(elapsed * 1000, 2)
            })
            print(f"[{checks}] ✅ {status} | {resp.status} | {elapsed*1000:.0f}ms")
        except Exception as e:
            elapsed = time.time() - start
            status = "DOWN"
            history.append({
                "time": datetime.now().isoformat(),
                "status": status,
                "error": str(e),
                "latency_ms": round(elapsed * 1000, 2)
            })
            print(f"[{checks}] ❌ {status} | {str(e)[:50]}")
        
        if max_checks is None or checks < max_checks:
            time.sleep(interval_seconds)
    
    return history
```

### 3.2 批量URL状态码检查
```python
import concurrent.futures

def check_urls(urls, max_workers=10):
    """并发检查多个URL的HTTP状态码"""
    def check_single(url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Checker/1.0"})
            resp = urllib.request.urlopen(req, timeout=5)
            return {"url": url, "status": resp.status, "error": None}
        except Exception as e:
            return {"url": url, "status": None, "error": str(e)}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(check_single, urls))
    
    return results
```

### 3.3 REST API客户端封装
```python
import json
import urllib.request
import urllib.error

class HttpClient:
    """轻量级HTTP客户端封装"""
    
    def __init__(self, base_url="", headers=None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {"Content-Type": "application/json"}
    
    def _request(self, method, path, data=None, params=None):
        url = self.base_url + path
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=self.headers, method=method)
        
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "message": e.reason}
    
    def get(self, path, params=None):
        return self._request("GET", path, params=params)
    
    def post(self, path, data=None):
        return self._request("POST", path, data=data)
    
    def put(self, path, data=None):
        return self._request("PUT", path, data=data)
    
    def delete(self, path):
        return self._request("DELETE", path)
```

### 3.4 简易网页爬虫
```python
import re
from html.parser import HTMLParser

class LinkExtractor(HTMLParser):
    """提取网页中的所有链接"""
    def __init__(self):
        super().__init__()
        self.links = []
    
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href and not href.startswith("#"):
                self.links.append(href)

def fetch_and_extract_links(url):
    """获取网页并提取所有链接"""
    req = urllib.request.Request(url, headers={"User-Agent": "CrawlerBot/1.0"})
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode()
    
    extractor = LinkExtractor()
    extractor.feed(html)
    
    return list(set(extractor.links))
```

### 3.5 速度测试工具
```python
import statistics

def speed_test(url, n=5):
    """测试URL的响应速度（n次采样）"""
    times = []
    for i in range(n):
        start = time.time()
        try:
            urllib.request.urlopen(url, timeout=10)
            times.append(time.time() - start)
        except Exception as e:
            times.append(None)
    
    valid_times = [t for t in times if t is not None]
    if not valid_times:
        return {"error": "所有请求均失败"}
    
    return {
        "url": url,
        "samples": n,
        "success_rate": f"{len(valid_times)/n*100:.1f}%",
        "min_ms": round(min(valid_times) * 1000),
        "max_ms": round(max(valid_times) * 1000),
        "avg_ms": round(statistics.mean(valid_times) * 1000),
        "median_ms": round(statistics.median(valid_times) * 1000),
    }
```

---

## 4. 自动化运维

### 4.1 定时任务调度器
```python
import threading
import signal

class SimpleScheduler:
    """轻量级定时任务调度器"""
    def __init__(self):
        self.jobs = []
        self.running = False
    
    def every(self, seconds):
        """装饰器：每隔seconds秒执行一次"""
        def decorator(func):
            self.jobs.append({"func": func, "interval": seconds, "last_run": 0})
            return func
        return decorator
    
    def start(self):
        self.running = True
        def loop():
            while self.running:
                now = time.time()
                for job in self.jobs:
                    if now - job["last_run"] >= job["interval"]:
                        try:
                            job["func"]()
                        except Exception as e:
                            print(f"任务错误: {e}")
                        job["last_run"] = now
                time.sleep(1)
        
        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
    
    def stop(self):
        self.running = False
```

### 4.2 进程守护
```python
import subprocess
import sys

def daemonize(command, restart_on_failure=True, max_restarts=5):
    """守护进程：监控并自动重启崩溃的程序"""
    restarts = 0
    
    while restarts < max_restarts:
        print(f"启动: {command}")
        proc = subprocess.Popen(command, shell=True)
        proc.wait()
        
        exit_code = proc.returncode
        print(f"进程退出: code={exit_code}")
        
        if not restart_on_failure:
            break
        
        restarts += 1
        print(f"重启中... ({restarts}/{max_restarts})")
        time.sleep(3)
    
    print(f"守护结束: 共重启{restarts}次")
```

### 4.3 磁盘使用监控
```python
import shutil

def check_disk_usage(path="/", threshold_percent=80):
    """检查磁盘使用率并在超过阈值时告警"""
    usage = shutil.disk_usage(path)
    percent = usage.used / usage.total * 100
    
    gb_used = usage.used / (1024**3)
    gb_total = usage.total / (1024**3)
    gb_free = usage.free / (1024**3)
    
    status = "⚠️ 告警" if percent > threshold_percent else "✅ 正常"
    
    print(f"磁盘: {path}")
    print(f"  已用: {gb_used:.1f}GB / {gb_total:.1f}GB ({percent:.1f}%)")
    print(f"  可用: {gb_free:.1f}GB")
    print(f"  状态: {status}")
    
    return {
        "total_gb": round(gb_total, 1),
        "used_gb": round(gb_used, 1),
        "free_gb": round(gb_free, 1),
        "percent": round(percent, 1),
        "alert": percent > threshold_percent
    }
```

### 4.4 日志轮转
```python
import gzip

def rotate_log(log_path, max_size_mb=100, keep=5):
    """日志轮转：压缩旧日志，保留最近N个"""
    if not os.path.exists(log_path):
        return
    
    size_mb = os.path.getsize(log_path) / (1024 * 1024)
    if size_mb < max_size_mb:
        return
    
    # 删除最旧的轮转文件
    for i in range(keep - 1, -1, -1):
        old_file = f"{log_path}.{i}.gz"
        new_file = f"{log_path}.{i+1}.gz"
        if os.path.exists(new_file):
            os.remove(new_file)
        if os.path.exists(old_file):
            os.rename(old_file, new_file)
    
    # 压缩当前日志
    gz_path = f"{log_path}.0.gz"
    with open(log_path, 'rb') as f_in:
        with gzip.open(gz_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    # 清空原日志
    open(log_path, 'w').close()
    print(f"✅ 日志已轮转: {log_path} → {gz_path}")
```

### 4.5 健康检查端点
```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time()
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # 静默模式

def run_health_server(port=8080):
    """启动简单的健康检查HTTP服务"""
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"🏥 健康检查服务: http://0.0.0.0:{port}/health")
    server.serve_forever()
```

---

## 5. 文本处理

### 5.1 中文分词统计
```python
import re
from collections import Counter

def chinese_word_frequency(text, top_n=20):
    """中文词频统计（简化版，基于字符n-gram）"""
    text = re.sub(r'[^\u4e00-\u9fff]', '', text)
    
    # 2-gram统计
    bigrams = [text[i:i+2] for i in range(len(text)-1)]
    counter = Counter(bigrams)
    
    print(f"总字符数: {len(text)}")
    print(f"独立词组: {len(counter)}")
    print(f"\nTop {top_n}:")
    for word, count in counter.most_common(top_n):
        print(f"  {word}: {count}")
    
    return counter.most_common(top_n)
```

### 5.2 Markdown转HTML
```python
import re

def markdown_to_html_basic(md_text):
    """基础Markdown转HTML（适合简单文档）"""
    html = md_text
    
    # 标题
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # 粗体和斜体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # 代码块和行内代码
    html = re.sub(r'```(\w*)\n(.+?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    
    # 链接和列表
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # 段落
    paragraphs = html.split('\n\n')
    html = '\n\n'.join(f'<p>{p.strip()}</p>' if not p.strip().startswith('<') else p for p in paragraphs)
    
    return html
```

### 5.3 文本差异比较
```python
import difflib

def text_diff(text1, text2, context_lines=3):
    """比较两段文本的差异"""
    diff = difflib.unified_diff(
        text1.splitlines(keepends=True),
        text2.splitlines(keepends=True),
        fromfile='原始版本',
        tofile='新版本',
        n=context_lines
    )
    return ''.join(diff)

def similarity_ratio(text1, text2):
    """计算两段文本的相似度"""
    return difflib.SequenceMatcher(None, text1, text2).ratio()
```

### 5.4 模板引擎
```python
import re

class SimpleTemplate:
    """极简模板引擎：{{ variable }} 替换"""
    
    def __init__(self, template_str):
        self.template = template_str
    
    def render(self, **kwargs):
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{{ {key} }}}}", str(value))
        return result
    
    @staticmethod
    def render_file(template_path, output_path, **kwargs):
        """从文件读取模板并渲染"""
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        result = template
        for key, value in kwargs.items():
            result = result.replace(f"{{{{ {key} }}}}", str(value))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        return result

# 使用示例
# tpl = SimpleTemplate("你好 {{ name }}，你有 {{ count }} 条新消息")
# print(tpl.render(name="张三", count=5))
```

### 5.5 敏感词过滤器
```python
class SensitiveWordFilter:
    """基于Trie树的敏感词过滤器"""
    
    def __init__(self):
        self.root = {}
    
    def add_word(self, word):
        node = self.root
        for char in word:
            node = node.setdefault(char, {})
        node['*'] = True  # 单词结束标记
    
    def add_words(self, words):
        for word in words:
            self.add_word(word)
    
    def filter(self, text, replace_char='*'):
        result = []
        i = 0
        while i < len(text):
            node = self.root
            j = i
            matched_len = 0
            while j < len(text) and text[j] in node:
                node = node[text[j]]
                j += 1
                if '*' in node:
                    matched_len = j - i
            if matched_len > 0:
                result.append(replace_char * matched_len)
                i += matched_len
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)
```

---

## 6. API工具

### 6.1 Flask/FastAPI快速启动
```python
# 最小Flask API服务
FLASK_TEMPLATE = '''
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/v1/echo", methods=["POST"])
def echo():
    data = request.get_json()
    return jsonify({"received": data, "timestamp": __import__("datetime").datetime.now().isoformat()})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
'''
```

### 6.2 API限流装饰器
```python
from functools import wraps
from collections import defaultdict

class RateLimiter:
    """基于滑动窗口的API限流器"""
    
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = defaultdict(list)
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(client_id=None, *args, **kwargs):
            now = time.time()
            cid = client_id or "default"
            
            # 清理过期记录
            self.clients[cid] = [t for t in self.clients[cid] if now - t < self.window_seconds]
            
            if len(self.clients[cid]) >= self.max_requests:
                raise Exception(f"请求过于频繁: {self.max_requests}次/{self.window_seconds}秒")
            
            self.clients[cid].append(now)
            return func(*args, **kwargs)
        return wrapper

# 使用示例
# rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
# @rate_limiter
# def my_api(client_id, data):
#     return process(data)
```

### 6.3 请求重试机制
```python
def retry(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """装饰器：自动重试失败的函数调用"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise
                    print(f"重试 {attempt+1}/{max_retries}: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
```

### 6.4 缓存装饰器
```python
from functools import lru_cache

def ttl_cache(ttl_seconds=300):
    """带TTL的缓存装饰器"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        
        def clear():
            cache.clear()
        
        wrapper.clear_cache = clear
        return wrapper
    return decorator
```

### 6.5 JSON Schema验证
```python
def validate_json_schema(data, schema):
    """简化版JSON Schema验证"""
    errors = []
    
    for field, rules in schema.items():
        # 必填检查
        if rules.get("required", False) and field not in data:
            errors.append(f"缺少必填字段: {field}")
            continue
        
        if field not in data:
            continue
        
        value = data[field]
        
        # 类型检查
        expected_type = rules.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"{field}: 需要字符串，实际为 {type(value).__name__}")
        elif expected_type == "number" and not isinstance(value, (int, float)):
            errors.append(f"{field}: 需要数字，实际为 {type(value).__name__}")
        elif expected_type == "list" and not isinstance(value, list):
            errors.append(f"{field}: 需要列表，实际为 {type(value).__name__}")
        
        # 范围检查
        if isinstance(value, (int, float)):
            if "min" in rules and value < rules["min"]:
                errors.append(f"{field}: 需要 >= {rules['min']}，实际 {value}")
            if "max" in rules and value > rules["max"]:
                errors.append(f"{field}: 需要 <= {rules['max']}，实际 {value}")
        
        # 长度检查
        if isinstance(value, str):
            if "min_length" in rules and len(value) < rules["min_length"]:
                errors.append(f"{field}: 长度需要 >= {rules['min_length']}")
            if "max_length" in rules and len(value) > rules["max_length"]:
                errors.append(f"{field}: 长度需要 <= {rules['max_length']}")
    
    return errors
```

---

## 版权和许可

© 2026 AI Startup Agent | 购买者可自由用于个人和商业项目
版本: v1.0 | 30+ 实用脚本 | 持续更新中
