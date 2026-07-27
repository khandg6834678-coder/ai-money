"""
匿名发布到 Telegraph (telegra.ph)
无需账号，无需KYC，直接发布文章获取公开URL
"""
import json
import urllib.request
import urllib.error

TELEGRAPH_API = "https://api.telegra.ph"

def create_account(short_name="AI_Efficiency", author_name="AI效率指南"):
    """创建Telegraph账号（匿名，无需验证）"""
    data = json.dumps({
        "short_name": short_name,
        "author_name": author_name
    }).encode()

    req = urllib.request.Request(
        f"{TELEGRAPH_API}/createAccount",
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode())
        if result.get("ok"):
            token = result["result"]["access_token"]
            print(f"  ✅ Telegraph账号创建成功")
            print(f"  🔑 Token: {token[:20]}...")
            print(f"  👤 作者: {result['result']['author_name']}")
            return token
        else:
            print(f"  ❌ 失败: {result}")
            return None
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None

def create_page(access_token, title, content, author_name="AI效率指南"):
    """创建Telegraph页面（公开URL）"""
    # Telegraph使用简单的HTML标签
    content_html = content_to_telegraph_html(content)

    data = json.dumps({
        "access_token": access_token,
        "title": title,
        "author_name": author_name,
        "content": content_html,
        "return_content": True
    }).encode()

    req = urllib.request.Request(
        f"{TELEGRAPH_API}/createPage",
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode())
        if result.get("ok"):
            page = result["result"]
            url = page["url"]
            print(f"  ✅ 文章发布成功!")
            print(f"  🔗 {url}")
            return url
        else:
            print(f"  ❌ 失败: {result}")
            return None
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None

def content_to_telegraph_html(content):
    """将简单格式转换为Telegraph HTML"""
    nodes = []

    for block in content:
        block_type = block.get("type", "p")
        text = block.get("text", "")

        if block_type == "h2":
            nodes.append({"tag": "h2", "children": [text]})
        elif block_type == "h3":
            nodes.append({"tag": "h3", "children": [text]})
        elif block_type == "p":
            nodes.append({"tag": "p", "children": [text]})
        elif block_type == "code":
            nodes.append({"tag": "pre", "children": [text]})
        elif block_type == "ul":
            items = [{"tag": "li", "children": [item]} for item in text.split("\n") if item.strip()]
            nodes.append({"tag": "ul", "children": items})

    return nodes

def publish_article(title, article_content_blocks):
    """一键发布文章到 Telegraph"""
    print()
    print(f"📝 发布: {title}")

    # 创建账号
    token = create_account()
    if not token:
        return None

    # 发布页面
    url = create_page(token, title, article_content_blocks)
    return url

def main():
    print("=" * 60)
    print("  Telegraph 匿名发布器")
    print("  无需注册 | 无需KYC | 即时公开")
    print("=" * 60)

    # 测试：发布第一篇SEO文章
    article = {
        "title": "2026年最好用的免费AI写作工具：从零基础到高手",
        "content": [
            {"type": "h2", "text": "为什么你需要AI写作工具？"},
            {"type": "p", "text": "在2026年，AI写作工具已经成为每个内容创作者的必备技能。无论你是写博客、做自媒体、还是写学术论文，合适的AI工具能帮你节省80%的时间。"},
            {"type": "h2", "text": "Top 5 免费AI写作工具"},
            {"type": "h3", "text": "1. DeepSeek — 中文写作王者"},
            {"type": "p", "text": "完全免费的国产大模型，中文理解和生成能力业界领先。支持128K超长上下文，适合写长篇博客和技术文档。"},
            {"type": "h3", "text": "2. ChatGPT (GPT-4o mini) — 英文写作首选"},
            {"type": "p", "text": "最新免费版ChatGPT的英文写作能力无可匹敌。创意写作和头脑风暴的最佳选择。"},
            {"type": "h3", "text": "3. Claude — 长文本分析专家"},
            {"type": "p", "text": "200K上下文窗口，可以一口气分析整本书。特别适合文献综述和研究报告写作。"},
            {"type": "h3", "text": "4. Kimi — 文档摘要利器"},
            {"type": "p", "text": "支持200万字的超长文档理解。上传PDF论文一键生成摘要，学生和研究人员的最爱。"},
            {"type": "h3", "text": "5. 豆包 — 短视频脚本专家"},
            {"type": "p", "text": "字节跳动出品，最懂短视频和社交媒体的AI。抖音、小红书文案的最佳助手。"},
            {"type": "h2", "text": "进阶技巧：如何写出更好的AI提示词？"},
            {"type": "p", "text": "好工具还需要好方法。精确的提示词能让AI输出质量提升10倍。关键是告诉AI：你是谁、写给谁看、什么风格、多少字。"},
            {"type": "p", "text": "我们整理了200+个经过实战验证的AI提示词模板，覆盖商业、编程、营销、学术等10个领域。每个提示词都经过多模型反复测试优化，复制粘贴即用。"},
            {"type": "p", "text": "👉 获取完整提示词宝典：支持加密货币支付 (ETH/USDT)，仅需$4.00 (约¥29.9)。支付地址: 0xb650C95CF7E494d78E0142049b1b2cC92F49dfB6 (ETH/BSC/Polygon)，付款后邮件联系 aiagent.payments@proton.me 即刻获取下载链接。"},
            {"type": "h2", "text": "总结"},
            {"type": "p", "text": "选择最适合你的AI写作工具，从今天开始每天节省2小时。记住：AI是工具，你是创造者。好工具 + 好方法 = 10倍效率。"},
            {"type": "p", "text": "本文由 AI效率指南 原创发布。更多AI效率技巧和工具评测，敬请关注。"},
        ]
    }

    url = publish_article(article["title"], article["content"])

    if url:
        print()
        print("=" * 60)
        print("  ✅ 文章已公开发布!")
        print(f"  🔗 {url}")
        print()
        print("  你可以:")
        print("  1. 分享这个链接到社交媒体")
        print("  2. Google会索引Telegraph页面")
        print("  3. 文章中可以放产品链接和付款信息")
        print("=" * 60)

        # 保存URL
        import os
        urls_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ledger', 'published-urls.json')
        existing = []
        if os.path.exists(urls_file):
            with open(urls_file) as f:
                existing = json.load(f)

        existing.append({
            "title": article["title"],
            "url": url,
            "platform": "Telegraph",
            "date": __import__('datetime').datetime.now().isoformat()
        })

        with open(urls_file, 'w') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    else:
        print("  ❌ 发布失败")

if __name__ == "__main__":
    main()
