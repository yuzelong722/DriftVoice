# 研声漂流 - 研究生匿名朋辈支持平台 MVP

基于PRD文档实现的研究生匿名朋辈支持平台MVP版本。
体验网址：https://driftvoice.onrender.com/

## 产品概述

研声漂流是一款面向研究生群体的匿名朋辈支持平台。用户可以匿名发布自己在研究生阶段遇到的困惑、压力或成长问题，系统根据问题类型、用户阶段与兴趣标签，将问题投递给可能具有相关经验的其他用户。接收者可选择是否匿名回复，回复内容默认仅提问者可见。提问者在收到回复后，可选择是否将问题和回复匿名公开，形成更广泛的讨论与经验沉淀。

## 核心功能（MVP）

根据PRD文档第9节MVP版本设计，本MVP实现以下核心功能：

### 已实现功能
1. **匿名提问** - 用户可以匿名发布问题
2. **问题分类** - 问题按模块分类（导师与课题组、科研与论文、职业规划等）
3. **系统投递** - 简化版随机投递机制
4. **匿名回复** - 接收者可以匿名回复问题
5. **提问者查看回复** - 提问者可以查看收到的回复
6. **感谢按钮** - 提问者可以感谢回复者
7. **举报按钮** - 用户可以举报不当内容
8. **管理员后台审核** - 基础的内容审核功能

### 暂未实现功能（根据PRD 9.2节）
- 复杂即时聊天
- 大规模公开广场
- 好友关系
- 私信
- 精细算法推荐
- 过度积分排行

## 技术栈

- **后端**: Python 3.14 + Flask 2.3
- **数据库**: SQLite 3（开发环境）
- **前端**: HTML5 + CSS3 + JavaScript（ES6+）
- **模板引擎**: Jinja2
- **CSS框架**: 自定义CSS（基于PRD要求的温和、安静、低刺激氛围设计）

## 安装与运行

### 环境要求
- Python 3.8+（当前使用Python 3.14）
- pip（Python包管理器）

### 安装步骤

1. **克隆或下载项目**
   ```bash
   cd /Users/yuzelong/CodeBuddy/20260605140513/app
   ```

2. **安装依赖**
   ```bash
   pip install flask flask-sqlalchemy
   ```
   
   或使用requirements.txt：
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化数据库**
   - 应用启动时会自动创建SQLite数据库（`gravelcho.db`）
   - 自动创建示例数据（用户、问题、回复、经验库条目）

4. **启动应用**
   ```bash
   python app.py
   ```
   
   应用将在 `http://0.0.0.0:5000` 启动

5. **访问应用**
   - 首页: http://localhost:5000/
   - 发布问题: http://localhost:5000/question/create
   - 待回应问题: http://localhost:5000/questions/pending
   - 我的回信: http://localhost:5000/my/messages
   - 经验库: http://localhost:5000/experience

## 项目结构

```
app/
├── app.py                  # 主应用文件（Flask应用、数据模型、路由）
├── templates/             # HTML模板
│   ├── base.html         # 基础模板
│   ├── index.html       # 首页
│   ├── create_question.html  # 发布问题页
│   ├── pending_questions.html # 待回应问题页
│   ├── create_reply.html      # 回复编辑页
│   ├── my_messages.html       # 我的回信页
│   └── experience_library.html # 经验库页
├── static/               # 静态文件
│   ├── css/
│   │   └── style.css     # 主样式文件
│   └── js/
│       └── main.js       # 主JavaScript文件
└── gravelcho.db         # SQLite数据库（自动创建）
```

## 数据库设计

基于PRD需求设计的数据模型：

### 用户表 (User)
- id: 主键
- anonymous_id: 匿名ID
- grade: 年级（研一、研二、研三、博士）
- major_category: 专业大类
- created_at: 创建时间

### 问题表 (Question)
- id: 主键
- user_id: 外键（提问者）
- title: 问题标题
- content: 问题内容
- category: 问题类型（一级模块）
- subcategory: 具体标签（二级标签）
- grade: 提问者阶段
- response_type: 希望收到的回应类型
- allow_public: 是否允许未来匿名公开
- is_risk: 是否涉及紧急风险
- is_public: 是否已公开
- status: 状态（open/closed）
- created_at: 创建时间

### 回复表 (Reply)
- id: 主键
- question_id: 外键（所属问题）
- user_id: 外键（回复者）
- content: 回复内容
- response_style: 回应风格
- is_read: 是否已读
- is_thanked: 是否已收到感谢
- created_at: 创建时间

### 经验库表 (Experience)
- id: 主键
- question_id: 外键（问题）
- reply_id: 外键（回复）
- category: 分类
- created_at: 创建时间

## API端点

### 问题相关
- `GET /api/questions/pending` - 获取待回应问题列表
- `GET /api/questions/<int:question_id>` - 获取问题详情及回复
- `POST /question/create` - 创建新问题（表单提交）
- `POST /api/questions/<int:question_id>/replies` - 创建回复

### 回复相关
- `POST /api/replies/<int:reply_id>/thank` - 感谢回复

### 经验库相关
- `GET /api/experiences` - 获取经验库列表

## PRD符合性说明

本MVP版本严格遵循PRD文档（研究生匿名朋辈支持平台 PRD 草案.docx）的要求：

### 符合PRD的功能实现
1. **产品定位** (PRD 2): 实现了匿名朋辈支持平台的核心定位
2. **核心功能** (PRD 7): 实现了7.1-7.10中MVP相关的核心功能
3. **用户流程** (PRD 8): 实现了提问流程、回复流程的基本版本
4. **MVP设计** (PRD 9): 严格按9.1节实现核心功能，按9.2节暂未实现非核心功能
5. **页面结构** (PRD 10): 实现了10.1-10.6节的所有页面
6. **安全提示**: 实现了风险识别与安全提示功能

### 需要补充的功能（未来版本）
1. **用户认证**: 如何验证用户为研究生（防止非目标用户进入）
2. **精细匹配算法**: 当前为简化版随机投递，未来可实现基于用户年级、专业、历史回复记录等的精细匹配
3. **内容审核自动化**: 当前为管理员后台审核，未来可增加AI辅助审核
4. **量化成功指标**: 根据PRD 9.3节，需要建立量化指标来衡量MVP验证目标

## 安全考虑

1. **匿名性保护**: 
   - 用户ID使用匿名ID
   - 回复者身份对提问者不可见
   - 公开时会去除可能暴露身份的信息

2. **内容安全**:
   - 风险关键词检测（自伤、自杀等）
   - 举报机制
   - 管理员审核

3. **数据安全**:
   - 使用SQLAlchemy ORM防止SQL注入
   - 表单验证防止XSS攻击

## 未来改进方向

1. **算法优化**: 实现更精细的问题-回复者匹配算法
2. **移动端优化**: 当前为桌面端设计，未来需优化移动端体验
3. **实时通知**: 实现邮件或站内信通知
4. **数据分析**: 添加数据分析功能，了解用户需求和行为模式
5. **多语言支持**: 考虑支持英文等其他语言

## 联系方式

如有问题或建议，请联系开发团队。

---
**注意**: 本平台提供朋辈支持，不能替代专业心理服务。如遇紧急情况，请及时联系学校心理中心、辅导员或拨打专业心理援助热线。
