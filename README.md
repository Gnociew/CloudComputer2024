# LangChain 数学解题原型系统

这是一个基于 **LangChain** + **Flask** + **SQLite** 的简单解题辅导系统原型示例，用于演示对中学数学基础题目的解题提示与答案验证，并将相关记录保存在数据库中。

## 项目背景

随着在线教育的普及，越来越多的学生依赖于网络平台来获取学习支持。传统的数学辅导往往依赖于教师的个别指导，而本项目通过智能化的方式，旨在为学生提供更为高效的学习支持。尤其是在中学阶段，学生面临的数学问题多样且复杂，及时的反馈和指导能够显著提高他们的学习效率和兴趣。

## 设计思路

本项目旨在为中学数学学生提供一个智能解题辅导系统，帮助他们在学习过程中获得及时的反馈和指导。设计思路主要包括以下几个方面：

1. **用户友好性**：系统界面简洁明了，学生可以轻松输入问题并获取提示，降低使用门槛。
2. **智能化**：通过调用大语言模型，系统能够生成个性化的解题提示和答案验证，提升学习效果。
3. **数据驱动**：通过记录学生的提问和答案，系统能够为教师提供有价值的数据，帮助他们了解学生的学习情况。

## 项目功能

### 1. 题目输入与理解
学生可以在前端界面输入中学数学题目（例如“2x + 3 = 7”）。系统会对输入的题目进行基本的格式验证，确保其符合数学表达式的标准。

### 2. 解题提示生成
后端通过 LangChain 调用大语言模型（如智谱 API），生成针对学生输入问题的解题提示。系统会提供分步解题的建议，而不是直接给出答案，以帮助学生理解解题过程。

### 3. 答案验证与反馈
学生提交答案后，系统会对答案进行验证。后端会调用大语言模型，判断学生的答案是否正确，并返回简要的反馈或提示，帮助学生了解错误的原因。

### 4. 数据存储
系统利用 SQLite 数据库将题目、提示、答案和验证结果等信息持久化存储，以便后续查询和分析。每次学生提交问题或答案时，相关记录都会被保存到数据库中，便于教师或系统管理员进行后续的统计和分析。

---
## 小组分工

- **付震宇**：
  - 负责需求分析和后端 API 实现（如题目输入、提示生成）。编写架构文档。对项目进行版本管理。
  - 负责与成员 2 一起进行后端架构设计，并处理数据库迁移和会话管理。
  - 配合其他成员完成系统集成和测试。负责撰写项目文档，总结项目开发过程

- **金彪**：
  - 负责数据库设计与迁移方案，确保 SQLite 数据库和 PostgreSQL 数据库的兼容性。负责云服务器的搭建与项目部署
  - 与成员 1 一起进行系统架构设计，实现后端API。优化数据库操作。
  - 配合其他成员进行系统集成和测试。负责撰写项目文档，总结项目开发过程

- **曾玮**：
  - 负责前端开发，确保用户界面简洁并且易于操作。
  - 负责图像生成功能的开发，确保方程图像生成与前端的兼容性。完成与后端的接口对接
  - 配合成员 1 和成员 2 进行系统集成和测试，确保前后端顺利对接。负责制作项目ppt

- **胡俊谦**：
  - 负责 LangChain 的集成与模型训练，确保解题提示生成和答案验证功能的准确性和高效性。
  - 调试 Prompt Template 和 LangChain 工作流。记录实验的相关问题与解决方案。
  - 协助其他成员进行系统集成和测试。

## 技术实现

本项目采用了以下技术栈：

1. **Flask**：作为后端框架，Flask 提供了轻量级的 Web 服务，支持快速开发和部署。
2. **LangChain**：用于与大语言模型进行交互，生成解题提示和验证答案。通过 LangChain，系统能够灵活调用不同的语言模型，满足不同的需求。
3. **SQLAlchemy**：作为 ORM（对象关系映射）工具，简化了数据库操作。通过 SQLAlchemy，项目能够方便地与 SQLite 数据库进行交互。
4. **SQLite**：用于存储题目、提示、答案和验证结果等数据，提供持久化存储。
5. **前端技术**：使用 HTML、CSS 和 JavaScript 构建用户界面，确保用户体验流畅。

前端使用 HTML、CSS 和 JavaScript 构建，主要技术实现包括：

1. **HTML**：构建页面的基本结构，包括输入框、按钮和结果显示区域。
2. **CSS**：使用内联样式定义页面的外观，确保界面美观且易于使用。
3. **JavaScript**：通过事件监听器处理用户的输入和按钮点击事件，使用 `fetch` API 发送 AJAX 请求与后端进行交互，获取解题提示、验证答案和生成图像。



## 项目结构

```bash
langchain-math-tutor/
│
├── .idea/                   # IDE 配置文件夹
│
├── backend/                 # 后端代码
│   ├── __pycache__          # Python 缓存文件夹
│   ├── .env                 # 环境变量配置文件
│   ├── database.py          # 数据库连接与会话管理
│   ├── db.sqlite            # SQLite 数据库文件
│   ├── db_migrate.py        # 数据库迁移脚本
│   ├── main.py              # Flask 后端主程序入口
│   ├── models.py            # SQLAlchemy 数据表模型定义
│   ├── PostgreSQL_db.py     # PostgreSQL 数据库连接
│   └── requirements.txt     # Python 依赖列表
│
├── frontend/                # 前端代码
│   └── index.html           # 前端网页 (HTML/JS/CSS)
├── 演示视频.mp4               # 演示视频
└── README.md                # 项目说明文件
```

---

## 环境与依赖

- **Python 3.8+**（建议 3.9 或更高）
- **Flask 2.2+**
- **LangChain 0.0.x**（具体版本可见 `requirements.txt`）
- **SQLAlchemy 2.0+**
- **OpenAI / 其他大模型**（如果要调用 GPT-3.5/4，需要设置环境变量 `OPENAI_API_KEY`）
- 浏览器（Chrome, Firefox, Edge, Safari 等）访问前端页面
---
## 以下是前端代码的关键部分：

```html
<!-- 输入题目 -->
<div class="section">
  <h2>1. 输入题目</h2>
  <textarea id="questionInput" placeholder="例如：2x + 3 = 7"></textarea>
  <button id="getHintBtn">获取解题提示</button>
  <div id="hintResult" class="result"></div>
</div>
```

```javascript
// 获取解题提示
document.getElementById('getHintBtn').addEventListener('click', async () => {
  const questionInput = document.getElementById('questionInput');
  const hintResult = document.getElementById('hintResult');

  const question = questionInput.value.trim();
  if (!question) {
    hintResult.textContent = '请输入题目内容！';
    return;
  }

  // 显示加载状态
  hintResult.textContent = '正在获取解题提示，请稍候...';

  try {
    const response = await fetch('/api/generate_hint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question })
    });
    const data = await response.json();

    if (data.error) {
      hintResult.textContent = `错误: ${data.error}`;
    } else {
      // 显示提示并保存 question_id
      hintResult.textContent = data.hint;
      currentQuestionId = data.question_id; // 保存后端返回的 question_id
    }
  } catch (error) {
    hintResult.textContent = '获取提示失败，请检查网络连接或联系管理员。';
    console.error('Error:', error);
  }
});
```
---

## 其他说明

### 持久化数据库

在 `database.py` 中，使用 SQLAlchemy 创建 SQLite 数据库引擎，并提供会话工厂：

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite')
engine = create_engine(f"sqlite:///{DB_FILE_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

### 数据库迁移

在 `db_migrate.py` 中，提供了从 SQLite 迁移到 PostgreSQL 的功能：

```python
import sqlite3
import psycopg2
from sqlalchemy import create_engine

# SQLite 和 PostgreSQL 连接设置
# 迁移逻辑...
```

### 模型定义

在 `models.py` 中，定义了 `QuestionRecord` 和 `AnswerRecord` 模型，用于存储题目和答案记录：

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text

Base = declarative_base()

class QuestionRecord(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    hint_text = Column(Text, nullable=True)

class AnswerRecord(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, nullable=False)
    student_answer = Column(Text, nullable=False)
    verification_result = Column(Text, nullable=True)
```

# `PostgreSQL_db.py` 介绍

`PostgreSQL_db.py` 文件用于配置和管理数据库连接，以及创建 SQLAlchemy 会话工厂。此文件定义了如何连接到 PostgreSQL 数据库，并提供会话功能以便进行数据库操作。

## 主要功能

1. **数据库连接配置**  
   文件中定义了连接阿里云 RDS 上的 PostgreSQL 数据库所需的配置信息。这些配置信息包括数据库主机地址、端口、用户名、密码和数据库名。

   连接字符串（`DATABASE_URL`）采用 PostgreSQL 的格式：
   ```python
   postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
   ```

2. **创建数据库引擎**  
   使用 SQLAlchemy 的 `create_engine` 方法创建一个数据库引擎。引擎负责与 PostgreSQL 数据库建立连接。通过设置 `echo=False`，可以避免输出 SQL 查询日志，减少日志干扰。

   ```python
   engine = create_engine(DATABASE_URL, echo=False)
   ```

3. **创建会话工厂**  
   使用 SQLAlchemy 的 `sessionmaker` 创建一个会话工厂（`SessionLocal`），会话工厂用于生成与数据库的会话对象。通过 `autoflush=False` 和 `autocommit=False` 参数，确保在事务提交前不会自动刷新数据，也不会自动提交事务。

   ```python
   SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
   ```

## 数据库连接配置

- **DB_HOST**: 数据库主机地址（此处为阿里云 RDS 实例的公网地址）
- **DB_PORT**: 数据库端口（PostgreSQL 默认端口为 5432）
- **DB_USER**: 数据库用户名
- **DB_PASSWORD**: 数据库密码
- **DB_NAME**: 数据库名称

例如，连接字符串格式为：
```bash
postgresql://gimpyo:Jinbiao0416@pgm-bp1ydqzg4937odnzxo.pg.rds.aliyuncs.com:5432/langchain
```

## 用法

在应用程序的其他部分，可以使用 `SessionLocal` 创建会话并与数据库进行交互。例如：

```python
from database import SessionLocal

# 创建数据库会话
db = SessionLocal()

# 执行数据库操作
# ...

# 提交事务
db.commit()

# 关闭会话
db.close()
```
---
### 主函数实现 main.py的介绍
## 核心功能

### 1. 解题提示生成（Hint Generation）

- **接口**: `/api/generate_hint` (POST)
- **功能**: 用户提交一个数学问题，系统调用 LangChain 生成分步解题提示。提示内容是简洁的解题步骤，而不是最终答案。
- **实现**:
  - 使用 LangChain 的 `LLMChain` 生成解题提示。
  - 生成的提示被保存到数据库的 `QuestionRecord` 表中，供后续查询。

代码片段：
```python
@app.route("/api/generate_hint", methods=["POST"])
def generate_hint():
    data = request.get_json()
    question_text = data.get("question", "").strip()
    if not question_text:
        return jsonify({"error": "No question provided"}), 400

    # 1. 调LangChain获取解题提示
    hint_result = hint_chain.run(question=question_text)

    # 2. 写入数据库
    db = SessionLocal()
    try:
        # 新建一条 QuestionRecord
        new_question = QuestionRecord(
            question_text=question_text,
            hint_text=hint_result.strip()
        )
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        question_id = new_question.id  # 获取新插入的ID
    finally:
        db.close()

    return jsonify({
        "question": question_text,
        "hint": hint_result.strip(),
        "question_id": question_id
    }), 200
```

### 2. 答案验证（Answer Verification）

- **接口**: `/api/verify_answer` (POST)
- **功能**: 用户提交问题和答案，系统验证答案的正确性并给出反馈（“正确”或“错误：原因”）。
- **实现**:
  - 使用 LangChain 进行答案验证，通过与经验丰富的数学老师角色对话判断答案的正确性。
  - 答案验证结果会被记录在数据库中的 `AnswerRecord` 表中。

代码片段：
```python
@app.route("/api/verify_answer", methods=["POST"])
def verify_answer():
    data = request.get_json()
    question_text = data.get("question", "").strip()
    student_answer = data.get("answer", "").strip()

    if not question_text or not student_answer:
        return jsonify({"error": "question or answer missing"}), 400

    # 1. 调LangChain进行答案验证
    verification_result = verify_chain.run(
        question=question_text,
        answer=student_answer
    ).strip()

    # 2. 查找对应 question_id（简单做法：根据 question_text 匹配最新一条）
    db = SessionLocal()
    try:
        # 先根据题目文本找到一个 QuestionRecord（此处简化为直接取最新）
        question_record = db.query(QuestionRecord)\
                            .filter(QuestionRecord.question_text == question_text)\
                            .order_by(QuestionRecord.id.desc())\
                            .first()

        question_id = question_record.id if question_record else None

        # 创建 AnswerRecord
        new_answer = AnswerRecord(
            question_id=question_id if question_id else 0,
            student_answer=student_answer,
            verification_result=verification_result
        )
        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)
    finally:
        db.close()

    return jsonify({
        "question": question_text,
        "student_answer": student_answer,
        "verification": verification_result
    }), 200
```

### 3. 方程图像生成（Equation Plotting）

- **接口**: `/api/plot_equation` (POST)
- **功能**: 用户提交一个数学方程，系统生成方程图像并返回给前端。
- **实现**:
  - 使用 Sympy 解析数学方程并求解方程的交点。
  - 使用 Matplotlib 绘制方程的图像，将图像转换为 Base64 编码并返回给前端，以便显示在网页中。

代码片段：
```python
@app.route("/api/plot_equation", methods=["POST"])
def plot_equation():
    data = request.get_json()
    equation = data.get("equation", "").strip()
    if not equation:
        return jsonify({"error": "No equation provided"}), 400

    # 预处理方程，将 '2x' 转换为 '2*x'
    equation = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation)

    # 分割方程为两个函数
    try:
        left_expr, right_expr = map(sympify, equation.split('='))
    except Exception as e:
        return jsonify({"error": f"Invalid equation: {str(e)}"}), 400

    x = Symbol('x')
    x_vals = np.linspace(-10, 10, 400)
    y_left = [left_expr.subs(x, val) for val in x_vals]
    y_right = [right_expr.subs(x, val) for val in x_vals]

    # 求交点
    intersection = solve(left_expr - right_expr, x)
    intersection_y = [left_expr.subs(x, val) for val in intersection]

    plt.figure()
    plt.plot(x_vals, y_left, label='Left Function')
    plt.plot(x_vals, y_right, label='Right Function')
    plt.scatter(intersection, intersection_y, color='red', zorder=5, label='Intersection')
    plt.title(f"Graph of {equation}")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()

    # 将图像保存到内存中
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return jsonify({"image": image_base64}), 200
```

## 数据库设计

- **数据库模型**: 使用 SQLAlchemy 定义数据库模型，包括 `QuestionRecord` 和 `AnswerRecord`。
  - `QuestionRecord` 存储问题文本和生成的解题提示。
  - `AnswerRecord` 存储学生提交的答案及其验证结果。

### 表结构

1. **QuestionRecord**
   - `id`: 唯一标识符
   - `question_text`: 数学问题文本
   - `hint_text`: 解题提示

2. **AnswerRecord**
   - `id`: 唯一标识符
   - `question_id`: 关联的 `QuestionRecord` 的 ID
   - `student_answer`: 学生提交的答案
   - `verification_result`: 答案验证结果（“正确”或“错误：原因”）

### API 接口（部分）

1. **解题提示生成**: `/api/generate_hint` (POST)
   - 请求数据:
     ```json
     {
       "question": "x^2 - 4 = 0"
     }
     ```
   - 返回数据:
     ```json
     {
       "question": "x^2 - 4 = 0",
       "hint": "首先将方程 x^2 = 4，接着求解 x 的值。",
       "question_id": 1
     }
     ```

2. **答案验证**: `/api/verify_answer` (POST)
   - 请求数据:
     ```json
     {
       "question": "x^2 - 4 = 0",
       "answer": "x = 2"
     }
     ```
   - 返回数据:
     ```json
     {
       "question": "x^2 - 4 = 0",
       "student_answer": "x = 2",
       "verification": "错误：答案应该是 x = ±2"
     }
     ```

3. **方程图像生成**: `/api/plot_equation` (POST)
   - 请求数据:
     ```json
     {
       "equation": "x^2 - 4 = 0"
     }
     ```
   - 返回数据:
     ```json
     {
       "image": "<base64_image_data>"
     }
     ```
---
---

## 本地运行

下面以 **Windows / Mac / Linux** 本地环境为例说明。

### 1. 克隆代码

```bash
git clone https://github.com/YourName/YourRepo.git
cd YourRepo
```

### 2. 安装依赖

进入 `backend` 目录，安装 Python 依赖：
```bash
cd backend
pip install -r requirements.txt
```
若需要，你也可以先创建并激活 Python 虚拟环境 (venv) 再进行安装。

### 3. 启动后端

确认 `main.py` 中有以下入口：
```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```
然后运行：
```bash
python main.py
```
Flask 将在 `http://127.0.0.1:5000` 启动服务器。首次运行时，会在同目录下自动创建 `db.sqlite` 数据库文件。

### 4. 测试访问

1. 直接打开浏览器访问 [http://127.0.0.1:5000](http://127.0.0.1:5000)，可看到后台默认返回的文本信息。  
2. 打开前端页面 `frontend/index.html`，在表单中输入题目、获取解题提示并提交答案。  
   - 如果前端和后端端口不同，需要在 `fetch` API 中指定后端地址，如 `http://127.0.0.1:5000/api/...`。

---

## 云端部署

### 1. 配置 RDS PostgreSQL 实例

1. **登录阿里云管理控制台**，进入 **RDS 管理控制台**。
2. 选择 **PostgreSQL 数据库实例**，获取连接信息：
   - **公网 IP**：pgm-bp1ydqzg4937odnzxo.pg.rds.aliyuncs.com
   - **数据库名称**：langchain
   - **用户名与密码**：gimpyo  Jinbiao0416

### 2. 配置 RDS 安全组

在阿里云控制台：

1. 进入 **RDS 安全组设置**。
2. 确保允许你的本地 IP 地址通过 5432 端口访问 PostgreSQL。

### 3. 本地 PostgreSQL 客户端连接

你可以直接通过本地的 PostgreSQL 客户端工具（如 `psql` 或 `pgAdmin`）来连接云端数据库。

#### 使用 `psql` 命令行连接：

```bash
psql -h <RDS 公网 IP> -p 5432 -U <用户名> -d <数据库名称>
```

例如：

```bash
psql -h 123.45.67.89 -p 5432 -U myuser -d mydatabase
```

系统会提示你输入密码。

### 3. 上传并配置项目

1. 在 `/home/youruser/` 或 `~/app` 下克隆 / 上传代码：
   ```bash
   cd ~
   mkdir app && cd app
   git clone https://github.com/YourName/YourRepo.git
   cd YourRepo/backend
   ```
2. （可选）创建 Python 虚拟环境并激活：
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 数据库自动创建：  
   - 只要 `main.py` 或 `models.py` 中有 `Base.metadata.create_all(bind=engine)` 逻辑，第一次启动时会自动生成 `db.sqlite` 文件。

### 4. 运行后端服务

```bash
python main.py
```
Flask 会在 `0.0.0.0:5000` 监听。如果你想后台持续运行，可以使用 `tmux`、`screen` 或 **Supervisor**。

### 5. 部署前端页面

- **最简单**：把 `frontend` 内容放在 Flask `static` 或直接用相对路径发送。  
- **Nginx 反向代理**（可选）：  
  - 安装并配置 Nginx，将域名或 IP 的 80 端口请求代理到 Flask 5000 端口；或者把静态页面放在 Nginx 的 `/var/www/html` 目录，再将 `/api/` 路径代理到 Flask。

### 6. 后台常驻运行（可选）

- 使用 **tmux / screen**：  
  启动 Flask 后即使关闭 SSH 也能保持运行。  
- 使用 **Supervisor** 或 **Systemd**：  
  配置守护进程自动启动、重启你的 Flask 程序。  
- 在 **Nginx** 中配置 HTTPS / 域名证书，提升访问安全。

---


### 模型调用

若使用 **OpenAI** API，需要设置环境变量 `OPENAI_API_KEY`，例如在 `.env` 文件或 ECS 环境变量里。  
若自建大模型 / Hugging Face 模型，也可以在 **LangChain** 里替换 LLM 接口。

---
