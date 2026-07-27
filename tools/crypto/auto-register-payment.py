"""
支付网关自动注册器
使用 mail.tm 临时邮箱 API 自动注册无KYC支付网关
"""
import json
import urllib.request
import urllib.error
import time
import random
import string
import os

LEDGER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ledger')
MAILTM_API = "https://api.mail.tm"

# ============================================
# Part 1: Mail.tm 临时邮箱
# ============================================

class TempEmail:
    """mail.tm 临时邮箱封装 — 无需API Key"""

    def __init__(self):
        self.address = None
        self.password = None
        self.token = None
        self.account_id = None

    def create(self, prefix="aiagent"):
        """创建临时邮箱"""
        # 1. 获取可用域名
        domains = self._request("GET", "/domains")
        if not domains:
            raise Exception(f"获取域名失败: 无响应")

        # 处理两种可能的响应格式
        if isinstance(domains, list):
            domain = domains[0]["domain"]
        elif "hydra:member" in domains:
            domain = domains["hydra:member"][0]["domain"]
        else:
            domain = domains.get("domain") or list(domains.values())[0][0]["domain"]

        # 2. 生成随机地址
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.address = f"{prefix}_{random_suffix}@{domain}"
        self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        # 3. 注册账号
        account = self._request("POST", "/accounts", {
            "address": self.address,
            "password": self.password
        })

        if not account or "id" not in account:
            raise Exception(f"创建邮箱失败: {account}")

        self.account_id = account["id"]
        print(f"  📧 临时邮箱: {self.address}")
        print(f"  🔑 ID: {self.account_id}")

        # 4. 获取Token
        self._get_token()
        return self

    def _get_token(self):
        """获取认证token"""
        token_resp = self._request("POST", "/token", {
            "address": self.address,
            "password": self.password
        })
        self.token = token_resp.get("token")
        return self.token

    def _request(self, method, path, data=None):
        """发送API请求"""
        url = MAILTM_API + path
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        body = json.dumps(data).encode() if data else None

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"  ⚠️ API错误 {e.code}: {error_body[:200]}")
            return None

    def check_inbox(self):
        """检查收件箱"""
        if not self.token:
            self._get_token()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        req = urllib.request.Request(
            f"{MAILTM_API}/messages",
            headers=headers
        )
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            messages = json.loads(resp.read().decode())
            return messages.get("hydra:member", [])
        except Exception as e:
            print(f"  ⚠️ 检查邮件失败: {e}")
            return []

    def wait_for_email(self, timeout_seconds=120, poll_interval=3):
        """等待新邮件到达"""
        print(f"  ⏳ 等待验证邮件... (最多{timeout_seconds}秒)")

        start = time.time()
        seen_ids = set()

        while time.time() - start < timeout_seconds:
            messages = self.check_inbox()

            for msg in messages:
                msg_id = msg.get("id")
                if msg_id not in seen_ids:
                    seen_ids.add(msg_id)
                    subject = msg.get("subject", "")
                    sender = msg.get("from", {}).get("address", "")

                    print(f"  📨 新邮件: {subject} (来自: {sender})")

                    # 获取邮件全文
                    full_msg = self._get_message(msg_id)

                    # 检查是否是验证邮件
                    if any(kw in subject.lower() for kw in
                           ["verify", "confirm", "验证", "确认", "activate", "welcome"]):
                        print(f"  ✅ 找到验证邮件!")
                        return full_msg

            time.sleep(poll_interval)

        print(f"  ⏰ 超时: 未收到验证邮件")
        return None

    def _get_message(self, msg_id):
        """获取邮件全文"""
        if not self.token:
            self._get_token()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        req = urllib.request.Request(
            f"{MAILTM_API}/messages/{msg_id}",
            headers=headers
        )
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            return json.loads(resp.read().decode())
        except Exception as e:
            print(f"  ⚠️ 获取邮件内容失败: {e}")
            return None

    def extract_verification_link(self, message):
        """从邮件中提取验证链接"""
        if not message:
            return None

        # 检查 html 和 text 部分
        html = ""
        text = ""

        if isinstance(message, dict):
            html = message.get("html", "") or ""
            text = message.get("text", "") or ""

        # 简单提取链接
        import re
        urls = re.findall(r'https?://[^\s<>"\']+', html + text)

        for url in urls:
            # 清理URL（去除尾部标点）
            url = url.rstrip('.,;:)')
            if any(kw in url.lower() for kw in
                   ["verify", "confirm", "activate", "验证", "确认"]):
                return url

        # 如果没找到特定验证链接，返回第一个URL
        return urls[0] if urls else None

    def cleanup(self):
        """删除临时邮箱"""
        if not self.token:
            return
        headers = {"Authorization": f"Bearer {self.token}"}
        req = urllib.request.Request(
            f"{MAILTM_API}/accounts/{self.account_id}",
            headers=headers,
            method="DELETE"
        )
        try:
            urllib.request.urlopen(req, timeout=10)
            print(f"  🗑️ 临时邮箱已删除")
        except Exception:
            pass


# ============================================
# Part 2: 支付网关注册
# ============================================

def try_register_orbchain(email_address, password):
    """尝试注册 OrbChain"""
    print()
    print("=" * 50)
    print("[OrbChain] 尝试注册...")
    print("=" * 50)

    # 注意: OrbChain 有 Cloudflare 保护
    # 可能需要绕过或使用其他API端点
    try:
        register_data = {
            "email": email_address,
            "password": password,
            "password_confirmation": password
        }

        req = urllib.request.Request(
            "https://orbchain.io/api/v1/auth/register",
            data=json.dumps(register_data).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            },
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode())
        print(f"  ✅ 注册成功: {result}")
        return result
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        print(f"  ⚠️ HTTP {e.code}: {error[:300]}")
        return None
    except Exception as e:
        print(f"  ❌ 连接失败 (可能有Cloudflare保护): {e}")
        return None

def try_register_wolvpay(email_address, password):
    """尝试注册 WolvPay"""
    print()
    print("=" * 50)
    print("[WolvPay] 尝试注册...")
    print("=" * 50)

    try:
        register_data = {
            "email": email_address,
            "password": password
        }

        req = urllib.request.Request(
            "https://www.wolvpay.com/api/v1/auth/register",
            data=json.dumps(register_data).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode())
        print(f"  ✅ 注册成功: {result}")
        return result
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        print(f"  ⚠️ HTTP {e.code}: {error[:300]}")
        return None
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")
        return None

def try_register_cryptopaycheckout(email_address, password):
    """尝试注册 CryptoPayCheckout"""
    print()
    print("=" * 50)
    print("[CryptoPayCheckout] 尝试注册...")
    print("=" * 50)

    try:
        register_data = {
            "email": email_address,
            "password": password
        }

        req = urllib.request.Request(
            "https://cryptopaycheckout.com/api/v1/auth/register",
            data=json.dumps(register_data).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode())
        print(f"  ✅ 注册成功: {result}")
        return result
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        print(f"  ⚠️ HTTP {e.code}: {error[:300]}")
        return None
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")
        return None


# ============================================
# Part 3: 主流程
# ============================================

def main():
    print()
    print("╔════════════════════════════════════════════╗")
    print("║  支付网关自动注册器                       ║")
    print("║  使用 mail.tm 临时邮箱 + API              ║")
    print("╚════════════════════════════════════════════╝")
    print()

    # Step 1: 创建临时邮箱
    print("[Step 1] 创建临时邮箱...")
    try:
        email = TempEmail()
        email.create(prefix="aistartup")
    except Exception as e:
        print(f"  ❌ 邮箱创建失败: {e}")
        print("  💡 备用方案: 手动在 mail.tm 创建邮箱")
        return

    email_addr = email.address
    email_pass = email.password
    print(f"  ✅ 邮箱就绪: {email_addr}")
    print()

    # Step 2: 尝试注册各支付网关
    results = {}

    # OrbChain
    orb_result = try_register_orbchain(email_addr, email_pass)
    if orb_result:
        results["orbchain"] = orb_result

    # WolvPay
    wolv_result = try_register_wolvpay(email_addr, email_pass)
    if wolv_result:
        results["wolvpay"] = wolv_result

    # CryptoPayCheckout
    cpc_result = try_register_cryptopaycheckout(email_addr, email_pass)
    if cpc_result:
        results["cryptopaycheckout"] = cpc_result

    # Step 3: 等待验证邮件
    if results:
        print()
        print("[Step 3] 等待验证邮件...")
        msg = email.wait_for_email(timeout_seconds=60)

        if msg:
            verify_link = email.extract_verification_link(msg)
            if verify_link:
                print(f"  🔗 验证链接: {verify_link}")

                # 尝试访问验证链接
                try:
                    req = urllib.request.Request(
                        verify_link,
                        headers={"User-Agent": "Mozilla/5.0"}
                    )
                    resp = urllib.request.urlopen(req, timeout=10)
                    print(f"  ✅ 验证成功: HTTP {resp.status}")
                except Exception as e:
                    print(f"  ⚠️ 验证链接访问失败: {e}")
                    print(f"  💡 链接可能需要浏览器打开: {verify_link}")

        # 保存注册结果
        save_path = os.path.join(LEDGER_DIR, 'payment-registrations.json')
        registration_record = {
            "email": email_addr,
            "password": email_pass,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": {k: "registered" for k in results},
            "verification_link": verify_link if msg else None
        }

        try:
            with open(save_path, 'w') as f:
                json.dump(registration_record, f, indent=2)
            print(f"\n  📁 注册记录已保存: {save_path}")
        except Exception:
            pass

    else:
        print()
        print("  ❌ 所有支付网关注册均失败")
        print()
        print("  可能原因:")
        print("  1. 网站使用了Cloudflare Bot保护")
        print("  2. API端点路径不正确")
        print("  3. 需要额外的验证（如CAPTCHA）")
        print()
        print("  💡 备用方案:")
        print("  - 使用临时邮箱手动注册（在浏览器中）")
        print(f"  - 邮箱: {email_addr}")
        print(f"  - 密码: {email_pass}")
        print("  - 注册后，将API Key更新到 ledger/payment-config.json")

    # 不删除邮箱，因为可能需要接收后续邮件
    print()
    print("=" * 50)
    print("  邮箱保留用于接收后续通知")
    print(f"  📧 {email_addr}")
    print(f"  💡 邮箱在 mail.tm 上约48小时后自动过期")
    print("=" * 50)

if __name__ == "__main__":
    main()
