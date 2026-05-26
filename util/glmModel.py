import os
import re
from pathlib import Path
from dotenv import load_dotenv
from zai import ZhipuAiClient

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _build_client() -> ZhipuAiClient:
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError("未读取到 ZHIPU_API_KEY，请在项目根目录 .env 中配置")
    return ZhipuAiClient(api_key=api_key)


def generate_job_match_report(position: str, company: str, profile_markdown: str) -> str:
    client = _build_client()
    prompt = f"""
你是一名资深招聘与职业发展顾问。请根据候选人资料与目标岗位，生成一份结构化中文岗位匹配报告。

【目标职位】{position}
【目标公司】{company}
【候选人资料（Markdown）】
{profile_markdown}

请严格按以下结构输出，使用 Markdown：
1. 总体匹配度（0-100）+ 一句话结论
2. 匹配亮点（3-5条）
3. 主要短板与提升（1-2条）


要求：
- 内容具体，不要空话；
- 明确提到候选人经历中的可迁移能力；
- 如果信息不足，指出缺失信息并说明影响。
""".strip()

    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "enabled"},
        max_tokens=8192,
        temperature=0.4,
    )
    return response.choices[0].message.content


def generate_styled_report_html(position: str, company: str, report_markdown: str) -> str:
    client = _build_client()
    prompt = f"""
你是一名前端视觉设计师。请把下面的岗位匹配 Markdown 报告转换为美观的 HTML 报告片段。

【目标职位】{position}
【目标公司】{company}
【Markdown 报告】
{report_markdown}

页面风格要求：
- 必须和个人主页保持一致：像素风、明亮、可爱但专业，使用卡片、像素边框、柔和粉蓝绿配色；
- 输出只包含一个 <article class="styled-job-report">...</article>，不要输出完整 HTML、head、body、script；
- 必须仿照下面 HTML 模板，只替换文本内容和列表项，不要改整体结构、class 名和层级；
- 结构必须清晰，包含顶部标题区、匹配度醒目展示、亮点、风险、建议区域；
- 不要使用外部 CDN、外部图片、JavaScript 或表单；
- 不要使用 Markdown 代码块包裹结果；
- 所有文本必须来自报告内容的合理整理，不要编造不存在的候选经历。

【HTML 模板样例】
<article class="styled-job-report">
  <section class="report-hero">
    <div>
      <p class="report-kicker">Job Match Test</p>
      <h2>目标岗位匹配报告</h2>
      <p class="report-summary">候选人与目标岗位具备较强相关性，测试开发、AI工具应用和项目推进经历可以形成主要竞争点。</p>
    </div>
    <div class="score-card">
      <span>匹配度</span>
      <strong>86</strong>
      <em>/100</em>
    </div>
  </section>

  <section class="report-grid">
    <div class="report-panel highlight-panel">
      <h3>匹配亮点</h3>
      <ul>
        <li><strong>测试开发基础：</strong>具备用例设计、接口测试、SQL 校验和缺陷跟踪经验。</li>
        <li><strong>AI 相关经历：</strong>参与 AI 分析助手、Agent 链路测试和 AI 生成测试用例推广。</li>
        <li><strong>项目推进能力：</strong>有系统配置、跨角色沟通和项目进度跟踪经验。</li>
      </ul>
    </div>

    <div class="report-panel risk-panel">
      <h3>短板与风险</h3>
      <ul>
        <li><strong>公司业务理解：</strong>需要补充目标公司的产品、业务线和岗位 JD 关键词。</li>
        <li><strong>技术深度呈现：</strong>建议强化自动化测试框架、接口工具链或代码能力证明。</li>
      </ul>
    </div>
  </section>

  <section class="report-panel advice-panel">
    <h3>简历优化建议</h3>
    <ol>
      <li>把与目标岗位最相关的实习经历提前，并用“动作 + 技术 + 结果”重写要点。</li>
      <li>突出 SQL、接口测试、Agent 测试、AI 测试用例生成等关键词。</li>
      <li>补充量化成果，例如用例数量、缺陷数量、效率提升或交付周期。</li>
    </ol>
  </section>

  <section class="report-panel interview-panel">
    <h3>面试准备方向</h3>
    <div class="prep-list">
      <p><strong>技术面：</strong>准备接口测试、SQL 校验、测试用例设计和缺陷定位案例。</p>
      <p><strong>业务面：</strong>梳理目标公司业务场景，并说明自己如何快速理解业务指标。</p>
      <p><strong>行为面：</strong>准备跨团队沟通、推动问题解决和项目交付相关故事。</p>
    </div>
  </section>
</article>
""".strip()

    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "enabled"},
        max_tokens=8192,
        temperature=0.35,
    )
    html = response.choices[0].message.content.strip()
    if html.startswith("```"):
        html = re.sub(r"^```(?:html)?\s*", "", html)
        html = re.sub(r"\s*```$", "", html).strip()
    article_match = re.search(r"<article\b[\s\S]*?</article>", html, re.IGNORECASE)
    if article_match:
        html = article_match.group(0)
    return html


def generate_job_match_report_package(position: str, company: str, profile_markdown: str) -> dict:
    report_markdown = generate_job_match_report(position, company, profile_markdown)
    report_html = generate_styled_report_html(position, company, report_markdown)
    return {
        "report_markdown": report_markdown,
        "report_html": report_html,
    }


if __name__ == "__main__":
    demo_text = "## 示例经历\n- 具备测试开发与项目管理经验。"
    print(generate_job_match_report_package("测试开发工程师", "某互联网公司", demo_text))
