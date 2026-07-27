"""
支付网关注册和 API 集成脚本
尝试通过编程方式注册无KYC支付网关
"""
import json
import urllib.request
import urllib.error
import os

WALLET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ledger')

def load_wallet():
    """加载钱包信息"""
    wallet_path = os.path.join(WALLET_DIR, 'wallet.json')
    with open(wallet_path, 'r') as f:
        return json.load(f)

def test_orbchain_api():
    """测试 OrbChain API 连接"""
    print("=" * 50)
    print("[OrbChain] 测试 API 连接...")
    print("=" * 50)

    # OrbChain 公开端点的基本测试
    try:
        req = urllib.request.Request(
            "https://orbchain.io/v1/ping",
            headers={"Accept": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"  ✅ 连接成功: {resp.status}")
        print(f"  响应: {resp.read().decode()[:200]}")
    except urllib.error.HTTPError as e:
        print(f"  ⚠️ HTTP错误: {e.code} - {e.reason}")
        print(f"  响应: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")

    print()
    print("📋 OrbChain 注册步骤:")
    print("  1. 访问 https://orbchain.io/register")
    print("  2. 输入邮箱和密码（无需KYC）")
    print("  3. 获取 API Key")
    print("  4. 更新下方配置中的 API Key")
    print()

def test_wolvpay_api():
    """测试 WolvPay API 连接"""
    print("=" * 50)
    print("[WolvPay] 测试 API 连接...")
    print("=" * 50)

    try:
        req = urllib.request.Request(
            "https://www.wolvpay.com/api/v1/status",
            headers={"Accept": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"  ✅ 连接成功: {resp.status}")
    except Exception as e:
        print(f"  ⚠️ 连接状态: {e}")

    print()
    print("📋 WolvPay 注册步骤:")
    print("  1. 访问 https://www.wolvpay.com/register")
    print("  2. 输入邮箱和密码（无需KYC）")
    print("  3. 添加钱包地址")
    print("  4. 在 Settings → API Keys 生成 Key")
    print()

def test_cryptopaycheckout_api():
    """测试 CryptoPayCheckout API"""
    print("=" * 50)
    print("[CryptoPayCheckout] 测试 API 连接...")
    print("=" * 50)

    try:
        req = urllib.request.Request(
            "https://cryptopaycheckout.com/api/v1/ping",
            headers={"Accept": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"  ✅ 连接成功: {resp.status}")
    except Exception as e:
        print(f"  ⚠️ 连接状态: {e}")

    print()
    print("📋 CryptoPayCheckout 注册步骤:")
    print("  1. 访问 https://cryptopaycheckout.com/register")
    print("  2. 输入邮箱（无需KYC，支持1000+币种）")
    print("  3. 设置你的收款钱包地址")
    print("  4. 获取 API Key")
    print()

def create_payment_integration_config():
    """创建支付集成配置文件"""
    wallet = load_wallet()
    eth_address = None
    for w in wallet.get('wallets', []):
        if w['chain'] == 'Ethereum':
            eth_address = w['address']
            break

    config = {
        "version": "1.0",
        "merchant_info": {
            "name": "AI Startup Agent",
            "email": "aiagent.payments@proton.me",
            "description": "Digital products and AI services"
        },
        "wallet_addresses": {
            "ETH": eth_address or "0xb650C95CF7E494d78E0142049b1b2cC92F49dfB6",
            "networks": ["Ethereum", "BSC", "Polygon", "Arbitrum", "Optimism", "Base"]
        },
        "payment_gateways": {
            "primary": {
                "name": "OrbChain",
                "api_endpoint": "https://orbchain.io/v1",
                "fee": "0.4%",
                "api_key": "YOUR_ORBCHAIN_API_KEY_HERE",
                "status": "pending_registration"
            },
            "backup": {
                "name": "WolvPay",
                "api_endpoint": "https://www.wolvpay.com/api/v1",
                "fee": "1%",
                "api_key": "YOUR_WOLVPAY_API_KEY_HERE",
                "status": "pending_registration"
            }
        },
        "products": [
            {
                "id": "prompt-bible-v1",
                "name": "AI Prompt Bible - 200+ Premium Prompts",
                "price_usd": 4.00,
                "price_cny": 29.9,
                "file": "ai-prompt-bible-200plus.md",
                "delivery": "instant_download"
            }
        ],
        "payment_flow": {
            "description": "Customer pays crypto → Gateway confirms → Deliver product",
            "supported_coins": ["USDT_BEP20", "USDC_BEP20", "ETH", "BTC_LN"],
            "recommended_for_small_payments": "BSC/BEP20 (fees < $0.10)"
        }
    }

    config_path = os.path.join(WALLET_DIR, 'payment-config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"支付配置已保存到: {config_path}")
    return config_path

def generate_payment_link_html():
    """生成可直接使用的付款链接HTML片段"""
    return '''
<!-- 将此片段嵌入任何销售页面 -->
<div class="crypto-payment-widget">
  <h3>使用加密货币付款</h3>
  <p>金额: ¥29.9 ≈ $4.00 USD</p>

  <!-- 方式1: 直接转账 -->
  <div class="payment-method">
    <h4>方式一: 直接转账（推荐 - 零手续费）</h4>
    <p>USDT/USDC (BSC/BEP20):</p>
    <code>0xb650C95CF7E494d78E0142049b1b2cC92F49dfB6</code>
    <p>付款后邮件通知: aiagent.payments@proton.me</p>
  </div>

  <!-- 方式2: OrbChain 托管支付 -->
  <div class="payment-method" style="margin-top:20px;">
    <h4>方式二: 支付网关（自动确认）</h4>
    <p>支持20+币种，由OrbChain提供技术支持</p>
    <button onclick="window.open('https://orbchain.io/pay?amount=4&currency=USD&merchant=aiagent','_blank')">
      通过OrbChain支付
    </button>
  </div>
</div>
'''

def main():
    print()
    print("=" * 60)
    print("  支付网关集成向导 - AI 创业代理")
    print("=" * 60)
    print()

    # 加载钱包
    wallet = load_wallet()
    eth_addr = None
    for w in wallet.get('wallets', []):
        if w['chain'] == 'Ethereum':
            eth_addr = w['address']
    print(f"💰 当前钱包: {eth_addr}")
    print()

    # 测试各支付网关
    test_orbchain_api()
    test_wolvpay_api()
    test_cryptopaycheckout_api()

    # 创建集成配置
    config_path = create_payment_integration_config()

    # 生成付款链接
    payment_html = generate_payment_link_html()
    html_path = os.path.join(WALLET_DIR, 'payment-widget.html')
    with open(html_path, 'w') as f:
        f.write(payment_html)
    print(f"付款组件已保存到: {html_path}")

    print()
    print("=" * 60)
    print("  ⚠️  需要手动完成的步骤:")
    print("=" * 60)
    print()
    print("由于支付网关需要邮箱验证码确认，以下步骤需要手动操作：")
    print()
    print("1️⃣  注册 OrbChain (推荐，0.4%费率):")
    print("   → 访问 https://orbchain.io/register")
    print("   → 使用邮箱: aiagent.payments@proton.me")
    print("   → 密码: [安全随机密码，建议保存到 ledger/credentials.txt]")
    print()
    print("2️⃣  获取 API Key 后更新配置:")
    print(f"   → 编辑: {config_path}")
    print("   → 替换 YOUR_ORBCHAIN_API_KEY_HERE")
    print()
    print("3️⃣  将钱包地址添加到支付网关后台:")
    print(f"   → ETH 地址: {eth_addr}")
    print()
    print("4️⃣  完成注册后，即可通过以下端点创建支付请求:")
    print("   → POST https://orbchain.io/v1/payment/invoice")
    print()

if __name__ == "__main__":
    main()
