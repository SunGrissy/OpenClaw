import subprocess, json

contents = json.dumps([
    {"key":"今日完成工作","sort":"0","content":"1. 硅基军团服务编排：启动小美(设计Advisor)并修复钉钉Stream鉴权401和CallbackMessage参数类型bug\n2. 组织架构调整：移除10人，新增刘兆蕊(特效)、刘品(实验)、王珂(运营)，标记多人状态\n3. dws CLI 安装授权：为OpenClaw配置钉钉工作台CLI工具\n4. Git巡检定时任务：配置12:30和22:30两次自动巡检","contentType":"markdown","type":"1"},
    {"key":"待完成工作","sort":"3","content":"1. 总管满满身份定义：给Hermes主profile补充SOUL.md角色身份\n2. 小美接LLM：当前硬编码模板回复，需接入Kimi等模型做真正推理\n3. OpenClaw watchdog：计划任务注册（需管理员权限）","contentType":"markdown","type":"1"},
    {"key":"需协助工作","sort":"4","content":"1. Hermes gateway稳定性：watchdog进程反复用--replace重启gateway，已杀掉watchdog但根因需确认","contentType":"markdown","type":"1"}
], ensure_ascii=False)

# Write to temp file for dws to read
with open(r"D:\OpenClaw\workspace\report_contents.json", "w", encoding="utf-8") as f:
    f.write(contents)

# Run dws with --dry-run first
result = subprocess.run(
    ["dws", "report", "create", 
     "--template-id", "153363afc40e225078a5a254ded82265",
     "--contents", contents,
     "--dry-run"],
    capture_output=True, text=True, timeout=30, encoding="utf-8"
)
print("STDOUT:", result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
print("STDERR:", result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
print("RC:", result.returncode)
