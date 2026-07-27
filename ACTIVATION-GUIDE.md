# 🔑 一次性激活指南

> 3 个步骤，约 5 分钟。做完后系统全自动运行。

---

## 第1步: 部署网站到 GitHub Pages (免费)

**目标**: 让内容站拥有公开 URL，被 Google 收录

### 1.1 创建 GitHub 仓库
1. 打开 https://github.com/new
2. Repository name 填: `ai-efficiency-guide`
3. 选择 **Public**
4. 不要勾选任何初始化选项
5. 点击 **Create repository**

### 1.2 推送代码
创建仓库后会看到一组命令，在你的终端执行：

```bash
cd /Users/2028act-azhangyunyao/Desktop/money/projects/content-site

# 初始化 git
git init
git add .
git commit -m "Initial: AI效率指南内容站"

# 关联远程仓库 (替换 YOUR_USERNAME 为你的 GitHub 用户名)
git remote add origin https://github.com/YOUR_USERNAME/ai-efficiency-guide.git
git branch -M main
git push -u origin main
```

### 1.3 启用 GitHub Pages
1. 打开仓库 → **Settings** → **Pages**
2. Source 选 **Deploy from a branch**
3. Branch 选 `main`，文件夹选 `/ (root)`
4. 点击 **Save**
5. 等待 1-2 分钟，页面会显示 `Your site is live at https://YOUR_USERNAME.github.io/ai-efficiency-guide/`

### 1.4 同样部署产品落地页（可选）
```bash
cd /Users/2028act-azhangyunyao/Desktop/money/projects/digital-products/marketing-assets
# 同上流程，仓库名: prompt-bible
```

> ⏱ 预计耗时: 2 分钟

---

## 第2步: 注册 OrbChain 支付网关 (0.4% 费率)

**目标**: 提供专业加密货币支付体验，自动确认交易

### 2.1 注册账号
1. 打开 https://orbchain.io
2. 点击 **Sign Up** 或 **Get Started**
3. 填写:
   - **Email**: 你可以用刚才生成的临时邮箱，或自己的邮箱
   - **Password**: 设置密码（12位以上）
4. 点击注册 → 检查邮箱 → 点击验证链接

### 2.2 获取 API Key
1. 登录后进入 **Dashboard**
2. 找到 **API Keys** 或 **Developers** 页面
3. 创建一个新的 API Key，权限选 **Full Access**
4. 复制生成的 Key（格式类似 `mk_live_xxxxx`）

### 2.3 配置到系统
```bash
# 将 API Key 写入配置
cd /Users/2028act-azhangyunyao/Desktop/money
python3 -c "
import json
with open('ledger/payment-config.json') as f:
    config = json.load(f)
config['payment_gateways']['primary']['api_key'] = 'YOUR_ORBCHAIN_API_KEY'
with open('ledger/payment-config.json', 'w') as f:
    json.dump(config, f, indent=2)
print('✅ API Key 已配置')
"
```

### 2.4 添加收款钱包地址
在 OrbChain 后台 Settings → Wallets 中添加:
- **ETH 地址**: `0xb650C95CF7E494d78E0142049b1b2cC92F49dfB6`
- 勾选自动结算

> ⏱ 预计耗时: 2 分钟

---

## 第3步: 创建 Dev.to 账号 (免费流量)

**目标**: 在开发者社区发布文章，获取初始流量

### 3.1 注册
1. 打开 https://dev.to/enter
2. 用 GitHub 账号直接登录 (或用邮箱注册)
3. 完成基础资料设置

### 3.2 获取 API Key
1. 登录后 → 右上角头像 → **Settings**
2. 左侧菜单 → **Extensions** 或直接访问 https://dev.to/settings/extensions
3. 在 **DEV Community API Keys** 区域
4. 创建一个新 Key，描述填 `AI Content Automation`
5. 复制 Key

### 3.3 可选: 同样注册 Medium
1. 打开 https://medium.com
2. 用 Google 或邮箱注册
3. Settings → Security and apps → Integration tokens
4. 创建一个 token

> ⏱ 预计耗时: 1 分钟

---

## ✅ 完成验证

三项都做完后，你应该拥有:

| 资源 | 值 |
|------|-----|
| 网站 URL | `https://YOUR_USERNAME.github.io/ai-efficiency-guide/` |
| OrbChain API Key | `mk_live_xxxx` |
| Dev.to API Key | 一个长字符串 |

**之后系统可以自动:**
- 批量生成 SEO 文章 → 自动发布到网站
- 创建付款链接 → 自动确认交易 → 自动发送产品
- 发布文章到 Dev.to → 获取搜索流量
- 追踪收入和开销 → 生成周报

---

## 🆘 遇到问题？

如果不方便做上述任何一步，**当前已经可以工作的部分**:
- 直接给对方 ETH 地址 `0xb650C95CF7E494d78E0142049b1b2cC92F49dfB6` 收款
- 付款后手动确认 → 系统自动交付产品
- 使用 `python3 tools/analytics/order-processor.py` 管理订单
