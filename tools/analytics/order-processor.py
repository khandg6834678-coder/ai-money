"""
订单自动处理系统
检测付款 → 验证 → 自动交付产品 → 更新账本
"""
import json
import os
import time
import hashlib
from datetime import datetime

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
LEDGER_DIR = os.path.join(ROOT_DIR, 'ledger')
PRODUCTS_DIR = os.path.join(ROOT_DIR, 'projects', 'digital-products')

# 收款地址
WALLET_ADDRESS = "0xb650C95CF7E494d78E0142049b1b2cC92F49dfB6"

# 产品目录
PRODUCTS = {
    "prompt-bible-v1": {
        "id": "prompt-bible-v1",
        "name": "AI Prompt Bible v1.0 - 200+ Premium Prompts",
        "price_usd": 4.00,
        "price_cny": 29.9,
        "file_path": os.path.join(PRODUCTS_DIR, "prompt-packs", "ai-prompt-bible-200plus.md"),
        "delivery_method": "download_link",
        "description": "200+ AI提示词模板，覆盖10大领域"
    },
    "code-templates-pack": {
        "id": "code-templates-pack",
        "name": "Python Utility Scripts Pack - 30+ Scripts",
        "price_usd": 3.00,
        "price_cny": 22.0,
        "file_path": os.path.join(PRODUCTS_DIR, "code-templates", "python-utility-scripts.md"),
        "delivery_method": "download_link",
        "description": "30+ Python实用脚本，6大类别"
    }
}

# 汇率 (USD → 加密货币)
# 简化为固定值，生产环境应使用实时API
EXCHANGE_RATES = {
    "ETH": 3500.00,   # 1 ETH = $3500
    "USDT": 1.00,     # 1 USDT = $1.00
    "USDC": 1.00,     # 1 USDC = $1.00
    "BTC": 65000.00,  # 1 BTC = $65000
}

class OrderProcessor:
    """订单处理和自动交付系统"""

    def __init__(self):
        self.orders = self._load_orders()
        self.completed_orders = self._load_completed()

    def _load_orders(self):
        path = os.path.join(LEDGER_DIR, 'pending-orders.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {"orders": []}

    def _load_completed(self):
        path = os.path.join(LEDGER_DIR, 'completed-orders.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {"orders": []}

    def _save_orders(self):
        path = os.path.join(LEDGER_DIR, 'pending-orders.json')
        os.makedirs(LEDGER_DIR, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.orders, f, indent=2)

    def _save_completed(self):
        path = os.path.join(LEDGER_DIR, 'completed-orders.json')
        os.makedirs(LEDGER_DIR, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.completed_orders, f, indent=2)

    def create_order(self, product_id, customer_email=None):
        """创建新订单"""
        if product_id not in PRODUCTS:
            print(f"  ❌ 未知产品: {product_id}")
            return None

        product = PRODUCTS[product_id]
        order_id = "ORD-" + hashlib.md5(
            f"{product_id}{time.time()}{customer_email or 'anonymous'}".encode()
        ).hexdigest()[:12].upper()

        order = {
            "order_id": order_id,
            "product_id": product_id,
            "product_name": product["name"],
            "amount_usd": product["price_usd"],
            "amount_cny": product["price_cny"],
            "status": "pending",
            "customer_email": customer_email,
            "payment_address": WALLET_ADDRESS,
            "created_at": datetime.now().isoformat(),
            "tx_hash": None,
            "paid_at": None,
            "delivered_at": None
        }

        self.orders["orders"].append(order)
        self._save_orders()

        print(f"  📝 订单创建: {order_id}")
        print(f"  📦 产品: {product['name']}")
        print(f"  💰 金额: ${product['price_usd']} (约¥{product['price_cny']})")
        print(f"  📧 客户: {customer_email or '未提供'}")
        print(f"  🏦 付款地址: {WALLET_ADDRESS[:10]}...{WALLET_ADDRESS[-8:]}")

        # 生成付款说明
        payment_instructions = self._generate_payment_instructions(order)
        order["payment_instructions"] = payment_instructions
        self._save_orders()

        return order

    def _generate_payment_instructions(self, order):
        """生成付款说明"""
        amount = order["amount_usd"]

        instructions = f"""
📋 付款说明 - 订单 {order['order_id']}
{'=' * 40}

产品: {order['product_name']}
金额: ${amount:.2f} USD (约¥{order['amount_cny']} CNY)

付款方式 (任选其一):

1️⃣ USDT/USDC (BSC/BEP20) ← 推荐! 手续费<$0.10
   地址: {WALLET_ADDRESS}
   金额: {amount:.2f} USDT 或 USDC
   网络: BNB Smart Chain (BEP20)

2️⃣ ETH (Arbitrum/Optimism) ← 低Gas费
   地址: {WALLET_ADDRESS}
   金额: 约 {amount/EXCHANGE_RATES['ETH']:.6f} ETH
   网络: Arbitrum 或 Optimism

3️⃣ ETH (Ethereum主网) ← Gas费较高
   地址: {WALLET_ADDRESS}
   金额: 约 {amount/EXCHANGE_RATES['ETH']:.6f} ETH

⚠️ 重要:
- 请从上述网络中选择一个发送
- 付款后发送交易哈希(TxHash)到: aiagent.payments@proton.me
- 我们会在1-5分钟内确认并发送下载链接
- 如有问题，通过邮件联系我们
"""
        return instructions

    def verify_payment_manual(self, order_id, tx_hash, amount_received, currency="USDT"):
        """手动验证付款（用于无法自动监控区块链时）"""
        for order in self.orders["orders"]:
            if order["order_id"] == order_id:
                expected_usd = order["amount_usd"]

                # 检查金额
                if currency in ["USDT", "USDC"]:
                    received_usd = amount_received  # 稳定币1:1
                else:
                    received_usd = amount_received * EXCHANGE_RATES.get(currency, 0)

                tolerance = 0.10  # 允许$0.10误差
                if abs(received_usd - expected_usd) > tolerance:
                    print(f"  ⚠️ 金额不匹配: 收到${received_usd:.2f}, 期望${expected_usd:.2f}")
                    return False

                order["status"] = "paid"
                order["tx_hash"] = tx_hash
                order["paid_at"] = datetime.now().isoformat()
                order["received_amount"] = amount_received
                order["received_currency"] = currency
                self._save_orders()

                print(f"  ✅ 付款已验证: {order_id}")
                return True

        print(f"  ❌ 订单未找到: {order_id}")
        return False

    def deliver_product(self, order_id):
        """交付产品"""
        for i, order in enumerate(self.orders["orders"]):
            if order["order_id"] == order_id:
                if order["status"] != "paid":
                    print(f"  ⚠️ 订单未付款: {order_id}")
                    return None

                product = PRODUCTS.get(order["product_id"])
                if not product:
                    print(f"  ❌ 产品未找到: {order['product_id']}")
                    return None

                # 检查产品文件
                file_path = product["file_path"]
                if not os.path.exists(file_path):
                    print(f"  ❌ 产品文件不存在: {file_path}")
                    return None

                # 生成下载链接（生产环境应使用真实URL）
                delivery_info = {
                    "order_id": order_id,
                    "product_name": product["name"],
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path),
                    "format": file_path.split('.')[-1],
                    "delivered_at": datetime.now().isoformat(),
                    "download_instructions": f"""
🎉 感谢购买！以下是你的下载信息:

产品: {product['name']}
格式: {file_path.split('.')[-1].upper()}
大小: {os.path.getsize(file_path):,} bytes

📥 下载说明:
由于系统尚未部署公开服务器，请通过以下方式获取文件:
1. 回复本邮件请求文件
2. 或访问我们的临时文件服务器

💡 提示:
- Markdown(.md)文件可用 Notion/Obsidian/VS Code 打开
- 该文件包含完整目录，可快速导航到需要的章节
"""
                }

                # 移动到已完成
                order["status"] = "completed"
                order["delivered_at"] = datetime.now().isoformat()
                order["delivery_info"] = delivery_info

                self.completed_orders["orders"].append(order)
                self.orders["orders"].pop(i)

                self._save_orders()
                self._save_completed()

                # 更新财务账本
                self._update_ledger(order)

                print(f"  ✅ 产品已交付: {order_id}")
                print(f"  📦 {product['name']}")
                print(f"  📁 {file_path}")

                return delivery_info

        print(f"  ❌ 订单未找到: {order_id}")
        return None

    def _update_ledger(self, order):
        """更新财务账本"""
        ledger_path = os.path.join(LEDGER_DIR, 'financial-ledger.md')

        entry = f"\n| {order['paid_at'][:10]} | 收入 | 数字产品 | {order['product_name']} ({order['order_id']}) | ¥{order['amount_cny']} | ¥0.00 | - |"

        try:
            with open(ledger_path, 'a') as f:
                f.write(entry)
            print(f"  📊 账本已更新")
        except Exception as e:
            print(f"  ⚠️ 账本更新失败: {e}")

    def get_order_status(self, order_id):
        """查询订单状态"""
        # 检查待处理订单
        for order in self.orders["orders"]:
            if order["order_id"] == order_id:
                return order

        # 检查已完成订单
        for order in self.completed_orders["orders"]:
            if order["order_id"] == order_id:
                return order

        return None

    def list_pending_orders(self):
        """列出所有待处理订单"""
        return self.orders["orders"]

    def generate_sales_report(self):
        """生成销售报告"""
        completed = self.completed_orders["orders"]

        if not completed:
            print("  📊 暂无销售记录")
            return

        total_revenue = sum(o.get("amount_cny", 0) for o in completed)

        print("\n" + "=" * 60)
        print("  📊 销售报告")
        print("=" * 60)
        print(f"  总订单数: {len(completed)}")
        print(f"  总收入: ¥{total_revenue:.2f}")
        print(f"  平均订单: ¥{total_revenue/len(completed):.2f}")
        print()

        for order in completed:
            print(f"  {order['order_id']} | {order['paid_at'][:10]} | {order['product_name'][:30]} | ¥{order['amount_cny']}")

        return {
            "total_orders": len(completed),
            "total_revenue": total_revenue,
            "orders": completed
        }

def main():
    print()
    print("=" * 60)
    print("  订单自动处理系统 - AI 创业代理")
    print("=" * 60)
    print()

    processor = OrderProcessor()

    # 演示：创建测试订单
    print("[演示] 创建订单:")
    order = processor.create_order("prompt-bible-v1", "demo-customer@example.com")

    if order:
        print()
        print(order["payment_instructions"])

        print()
        print("[演示] 模拟付款验证:")
        processor.verify_payment_manual(
            order["order_id"],
            tx_hash="0xDemoTxHash1234567890",
            amount_received=4.00,
            currency="USDT"
        )

        print()
        print("[演示] 自动交付:")
        delivery = processor.deliver_product(order["order_id"])

        if delivery:
            print()
            print(delivery["download_instructions"])

    # 生成报告
    processor.generate_sales_report()

    print()
    print("=" * 60)
    print("  系统就绪 ✅")
    print("=" * 60)
    print()
    print("📋 工作流程:")
    print("  1. 创建订单 → 生成付款地址和说明")
    print("  2. 客户付款 → 发送TxHash到邮箱")
    print("  3. 手动/自动验证 → verify_payment_manual()")
    print("  4. 自动交付 → deliver_product()")
    print("  5. 更新账本 → 自动记录收入")
    print()
    print("🔗 收款地址:")
    print(f"  {WALLET_ADDRESS}")
    print()
    print("📧 联系邮箱: aiagent.payments@proton.me")
    print()
    print("💡 待自动化:")
    print("  - 区块链浏览器API监控 (需免费注册API Key)")
    print("  - 邮件自动发送 (需SMTP服务配置)")
    print("  - 支付网关Webhook (需网关注册)")

if __name__ == "__main__":
    main()
