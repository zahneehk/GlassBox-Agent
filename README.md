# 📦 GlassBox-Agent

[English](#english-version) | [中文版](#chinese-version)

---

<a name="english-version"></a>
## 🇬🇧 English Version

**A transparent, agent-driven visual execution system.**

GlassBox-Agent is a "white-box" execution engine designed for the next generation of AI applications. 

Traditional LLM automation tools often operate as a black box where users can only wait for the final output. GlassBox-Agent aims to break this paradigm. It strictly decouples the "decision-making brain" (e.g., OpenClaw) from the "executing limbs" (Playwright), introducing a powerful Orchestrator layer in between. 

In this system, every Agent runs in a fully isolated Docker container. Through integrated `x11vnc` and `noVNC` technologies, users can watch real-time, live-stream-like execution of multiple Agents operating on actual web pages via a custom Web UI. This not only physicalizes LLM capabilities but also ensures the safety of high-risk tasks through system-level Human-in-the-loop (HITL) mechanisms.

### ✨ Value Proposition
1. **Capability Transformation**: Converts an LLM's text-generation ability into executable actions in the digital world.
2. **White-Box Observability**: Transforms black-box automation into a transparent system that is observable, interruptible, and replayable.
3. **Architectural Decoupling**: The upper-layer LLM handles uncertain reasoning, the lower-layer Playwright handles deterministic execution, and the Orchestrator manages isolation and scheduling.

### 🏗️ High-Level Architecture

```text
[ Custom Web UI ]  <-- (Renders noVNC stream & receives user input)
       │
[ Nginx / API Gateway ] <-- (HTTP Routing & WebSocket Dynamic Proxying)
       │
===================================================================
       │
[ OpenClaw (Agent Layer) ] <-- (Multi-Agent Collaboration / Planner / Executor / Reviewer)
       │    └─ Outputs structured JSON Plans
       ▼
[ Orchestrator (Scheduling) ] <-- (FastAPI + Redis + PostgreSQL)
       │    ├─ Task breakdown & dispatching
       │    ├─ State machine management & Policy interception
       │    └─ Container Lifecycle Management (GC)
       ▼
===================================================================
       │
[ Container Workspace ] <-- (Isolated Docker Container Cluster)
       │    ├─ Node.js Runner 
       │    ├─ Playwright (Browser Automation)
       │    └─ Xvfb + x11vnc + noVNC (Desktop Environment & Streaming)
       ▼
[ Target Web Environment ] 
```

### 🧩 Core Components
* **Agent Layer (OpenClaw)**: The "Brain". It does not operate the browser directly but makes logic and reasoning decisions via Prompts and Skills, outputting standardized JSON actions (e.g., `{"action": "click", "target": "login"}`).
* **Orchestrator Layer**: The "Central Nervous System". Built with FastAPI, Redis, and PostgreSQL. It buffers the LLM's uncertainty, dispatches tasks to specific isolated containers, and cleans complex state data (like massive DOM trees) before sending them back to the Agent.
* **Execution Layer (Container Workspace)**: The "Limbs". Each Agent instance corresponds to a fully isolated Docker container (Cookie, Session, Storage, Profile are physically isolated). Playwright only executes pre-defined template actions to ensure deterministic execution.

### 💡 Key Technical Decisions
* **Container Isolation over Playwright Context**: Provides a true "independent workspace" mental model, makes it easier to allocate specific CPU/Memory limits to prevent host OOM, and is much friendlier for setting up independent X11 desktop streams.
* **Visualization via noVNC**: Bypasses slow screenshot-polling methods. The flow (`Xvfb → x11vnc → websockify → noVNC`) maps the X11 desktop directly to the browser via WebSockets for low-latency, interactive monitoring.
* **Human-in-the-loop (HITL)**: Risk control is not done via prompting. If a step is marked as `step.risk == "high"`, the Orchestrator pauses execution and pushes a WebSocket request to the UI. The container resumes only after explicit human authorization.

---

<a name="chinese-version"></a>
## 🇨🇳 中文版

**一个透明的 Agent 驱动可视化执行系统。**

GlassBox-Agent 是一款面向下一代 AI 应用的“白盒化”执行引擎。

传统的大模型自动化工具往往是一个黑盒（Blackbox），用户只能等待最终结果。而 GlassBox-Agent 旨在打破这一现状。它将系统的“决策大脑（如 OpenClaw）”与“执行手脚（Playwright）”彻底解耦，并在中间引入了强大的 Orchestrator 调度层。

在这里，每一个 Agent 都在完全隔离的 Docker 容器中运行。通过集成的 `x11vnc` 与 `noVNC` 技术，用户可以在自定义的 Web UI 中，像观看直播一样实时看到多个 Agent 在真实网页上的每一个操作细节。这不仅实现了大模型能力的“物理转化”，更通过系统级的 Human-in-the-loop（人工介入）机制，保障了高风险任务的安全可控。

### ✨ 核心价值
1. **能力转化**：将 LLM 的“生成文本能力”转化为物理世界/数字世界的“可执行操作能力”。
2. **白盒可观测**：将传统自动化的黑盒转化为**可视化执行、可中断、可回放**的透明系统。
3. **架构解耦**：上层 LLM 负责不确定的推理决策，下层 Playwright 负责确定性的动作执行，中间层 Orchestrator 负责隔离与调度。

### 🏗️ 整体架构

```text
[ 自定义 Web UI ]  <-- (呈现 noVNC 实时流 & 接收用户指令)
       │
[ Nginx / API Gateway ] <-- (HTTP 路由 & WebSocket 动态代理)
       │
===================================================================
       │
[ OpenClaw (Agent 层) ] <-- (多 Agent 协作 / Planner / Executor / Reviewer)
       │    └─ 输出结构化任务 (JSON Plan)
       ▼
[ Orchestrator (调度层) ] <-- (FastAPI + Redis + PostgreSQL)
       │    ├─ 任务拆解与分发
       │    ├─ 状态机管理与安全拦截 (Policy)
       │    └─ 容器生命周期管理 (GC)
       ▼
===================================================================
       │
[ Container Workspace (执行层) ] <-- (独立的 Docker 容器集群)
       │    ├─ Node.js Runner (执行器)
       │    ├─ Playwright (浏览器自动化)
       │    └─ Xvfb + x11vnc + noVNC (桌面环境与流媒体化)
       ▼
[ Target Web Environment ] 
```

### 🧩 核心组件说明
* **Agent 层 (OpenClaw)**：大脑。不直接操作浏览器，仅通过 Prompt 和预设的 Skills 进行逻辑推理和决策，输出标准化的 JSON 动作指令。
* **调度层 (Orchestrator)**：中枢神经。采用 FastAPI + Redis + PostgreSQL 技术栈。负责任务拆解分发、追踪状态，并在接收底层庞大的 DOM 树/截图后提取关键信息回传，避免撑爆 LLM 的上下文窗口。
* **执行层 (Container Workspace)**：手脚。每个 Agent 实例对应一个完全隔离的 Docker 容器。Cookie、Session 等实现物理隔离。Playwright 仅执行预设的模板化 Action，保证确定性。

### 💡 关键技术决策
* **容器隔离 > Playwright Context**：完美符合“独立工作空间”的心智模型，方便搭建独立的 X11 虚拟桌面进行串流，并可以通过 Orchestrator 设定明确的硬件配额，防止宿主机 OOM。
* **可视化方案 (noVNC)**：技术流向为 `Xvfb → x11vnc → websockify → noVNC`。延迟极低，交互完整，直接将 X11 桌面通过 WebSocket 映射到用户的自建 UI 中。
* **系统级中断 (Human-in-the-loop)**：当 Orchestrator 评估当前 Step 标记为高风险时（`step.risk == "high"`），调度器主动暂停执行，并通过 WebSocket 向前端推送确认请求，用户授权后方可继续。
