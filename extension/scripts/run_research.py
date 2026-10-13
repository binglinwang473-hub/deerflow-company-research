"""用 DeerFlow 的嵌入式客户端运行“求职者公司调研”。
用法: uv run --project ../upstream/backend python run_research.py 字节跳动 AI产品经理
密钥从 /workspace/ai-job-radar/.env 的 LLM_API_KEY 读取，只放进进程环境变量，不打印不落盘。
"""
import datetime, os, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
EXT = HERE.parent
ROOT = EXT.parent

def load_key():
    for line in open(os.environ.get("KEY_ENV_FILE", "/workspace/ai-job-radar/.env")):
        line = line.strip().removeprefix("export ").strip()
        if line.startswith("LLM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("LLM_API_KEY not found")

os.environ["DEEPSEEK_API_KEY"] = load_key()
os.environ.setdefault("DEER_FLOW_CONFIG_PATH", str(EXT / "config.yaml"))
os.environ.setdefault("DEER_FLOW_HOME", str(EXT / ".deer-flow-home"))

sys.path.insert(0, str(EXT))
sys.path.insert(0, str(EXT))
from deerflow.client import DeerFlowClient  # noqa: E402

company, role = sys.argv[1], sys.argv[2]
skill = (EXT / "skills/job-seeker-company-research/SKILL.md").read_text()
today = datetime.date.today().isoformat()
prompt = f"""请严格按照下面这个技能说明执行任务。今天是 {today}。

<skill>
{skill}
</skill>

任务：公司 = {company}；目标岗位 = {role}。
完成检索后，直接在回复里输出完整 Markdown 报告（不要写文件，不要省略章节）。"""

client = DeerFlowClient(model_name="deepseek-chat", thinking_enabled=False)
report = client.chat(prompt, thread_id=f"company-research-{datetime.datetime.now():%Y%m%d%H%M%S}")
i = report.find("# ")
if i > 0:
    report = report[i:]  # 去掉模型的开场白
report = report.replace("---\n\n**几点提醒**", "---\n\n**几点提醒**")
out = ROOT / "reports" / f"{company}_{role}_{today}.md"
out.write_text(report)
print("saved:", out, "chars:", len(report))
