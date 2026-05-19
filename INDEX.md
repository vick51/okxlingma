# OKX量化交易系统 - 文档索引

欢迎使用OKX量化交易系统！本文档索引帮助您快速找到所需信息。

---

## 📚 文档导航

### 🚀 新手入门
- **[QUICK_START.md](QUICK_START.md)** - ⭐ **从这里开始**
  - 3分钟快速启动指南
  - 常用命令速查
  - 故障排查指南

### 📖 完整文档
- **[README.md](README.md)** - 📘 **主要文档**
  - 项目介绍和功能特性
  - 详细的安装和配置说明
  - 交易策略说明
  - Web界面功能介绍
  - 常见问题解答

### 📋 部署指南
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - ✅ **部署必备**
  - 部署前检查清单
  - 逐步部署指南
  - 验证清单
  - 常见问题处理
  - 性能优化建议
  - 安全加固指南
  - 备份和维护策略

### 💻 开发文档
- **[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)** - 🔧 **技术细节**
  - 技术选型说明
  - 系统架构设计
  - 核心交易策略代码示例
  - 数据库设计
  - API接口定义
  - Docker部署方案

### 📝 需求文档
- **[REQUIREMENTS.md](REQUIREMENTS.md)** - 📊 **需求规格**
  - 项目概述和目标
  - 功能需求详细说明
  - 非功能需求
  - 技术架构
  - 开发计划

### 📊 项目总结
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 🎯 **项目概览**
  - 已完成功能清单
  - 技术栈说明
  - 项目结构
  - 资源占用情况
  - 下一步建议

---

## 🗂️ 项目文件结构

```
okx-trading-system/
│
├── 📘 文档 (Documentation)
│   ├── INDEX.md                     ← 您在这里（文档索引）
│   ├── QUICK_START.md              ← 新手从这里开始
│   ├── README.md                   ← 主要文档
│   ├── DEPLOYMENT_CHECKLIST.md     ← 部署指南
│   ├── DEVELOPMENT_PLAN.md         ← 开发文档
│   ├── REQUIREMENTS.md             ← 需求文档
│   └── PROJECT_SUMMARY.md          ← 项目总结
│
├── ⚙️ 配置文件 (Configuration)
│   ├── .env.example                ← 环境变量示例（复制为.env）
│   ├── config.py                   ← 配置管理
│   ├── requirements.txt            ← Python依赖
│   ├── .gitignore                  ← Git忽略文件
│   └── .dockerignore               ← Docker忽略文件
│
├── 🐳 Docker配置 (Docker)
│   ├── Dockerfile                  ← Docker镜像定义
│   ├── docker-compose.yml          ← Docker编排
│   ├── start.sh                    ← Linux启动脚本
│   └── stop.sh                     ← Windows停止脚本
│
├── 🐍 Python代码 (Python Code)
│   ├── app.py                      ← Flask主应用
│   │
│   ├── trading/                    ← 交易模块
│   │   ├── okx_client.py           ← OKX API封装
│   │   ├── strategy.py             ← 交易策略引擎
│   │   └── indicators.py           ← 技术指标计算
│   │
│   ├── database/                   ← 数据库模块
│   │   └── db_manager.py           ← SQLite管理
│   │
│   └── utils/                      ← 工具模块
│       ├── logger.py               ← 日志管理
│       └── email_sender.py         ← 邮件发送
│
├── 🌐 Web前端 (Web Frontend)
│   └── web/
│       ├── templates/
│       │   └── index.html          ← 主页面
│       └── static/
│           ├── css/
│           │   └── style.css       ← 样式文件
│           └── js/
│               └── app.js          ← 前端逻辑
│
└── 💾 数据目录 (Data - 运行时生成)
    └── data/
        ├── trading.db              ← SQLite数据库
        └── trading.log             ← 日志文件
```

---

## 🎯 快速查找

### 我想...

#### 开始使用系统
→ 阅读 [QUICK_START.md](QUICK_START.md)

#### 了解系统功能
→ 阅读 [README.md](README.md) 的"功能特性"章节

#### 部署系统
→ 按照 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) 操作

#### 修改交易参数
→ 查看 [README.md](README.md) 的"修改配置"章节

#### 理解交易策略
→ 阅读 [README.md](README.md) 的"交易策略说明"章节

#### 查看API接口
→ 阅读 [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) 的"API接口"章节

#### 了解数据库结构
→ 阅读 [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) 的"数据库设计"章节

#### 排查问题
→ 查看 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) 的"常见问题处理"章节

#### 备份数据
→ 阅读 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) 的"备份策略"章节

#### 贡献代码
→ 阅读 [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) 了解代码结构

---

## 📞 获取帮助

### 遇到问题？

1. **首先查看日志**
   ```bash
   docker-compose logs -f
   ```

2. **查阅文档**
   - 常见问题: [README.md](README.md) 的"常见问题"章节
   - 故障排查: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) 的"常见问题处理"章节

3. **检查配置**
   - 确认 `.env` 文件正确配置
   - 确认API密钥有效
   - 确认网络连接正常

---

## 🚀 快速命令参考

```bash
# 启动系统
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止系统
docker-compose down

# 重启系统
docker-compose restart

# 查看状态
docker-compose ps

# 备份数据库
cp data/trading.db data/trading.db.backup.$(date +%Y%m%d)

# 进入容器
docker exec -it okx-trading-system bash
```

---

## 📊 系统概览

### 核心功能
- ✅ 自动化MACD策略交易
- ✅ 实时持仓监控
- ✅ 历史交易查询
- ✅ 邮件通知
- ✅ Web可视化界面

### 技术栈
- **后端**: Flask + ccxt + SQLite
- **前端**: 原生HTML/CSS/JS + Chart.js
- **部署**: Docker + Docker Compose
- **指标**: MACD (15分钟周期)

### 资源占用
- **内存**: ~150-200 MB
- **CPU**: <5% (空闲), <20% (交易时)
- **磁盘**: ~50 MB

---

## 🎓 学习路径

### 第1天: 了解和部署
1. 阅读 [QUICK_START.md](QUICK_START.md)
2. 配置环境变量
3. 启动系统
4. 访问Web界面

### 第2天: 理解和测试
1. 阅读 [README.md](README.md) 了解功能
2. 观察策略执行
3. 检查邮件通知
4. 测试各项功能

### 第3天: 定制和优化
1. 根据需要调整参数
2. 阅读 [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) 了解技术细节
3. 设置备份策略
4. 优化配置

### 持续: 监控和维护
1. 定期检查日志
2. 监控策略表现
3. 备份数据
4. 更新系统

---

## ⚠️ 重要提醒

### 安全第一
- 🔐 妥善保管API密钥
- 🔐 不要将 `.env` 文件提交到Git
- 🔐 定期更改密码
- 🔐 启用IP白名单（如果可能）

### 风险控制
- ⚡ 先在模拟盘测试
- ⚡ 从小仓位开始
- ⚡ 设置止损机制
- ⚡ 密切监控策略表现

### 数据备份
- 💾 定期备份数据库
- 💾 保存重要配置文件
- 💾 记录交易日志

---

## 📈 下一步

现在您已经了解了文档结构，建议：

1. **立即开始**: 打开 [QUICK_START.md](QUICK_START.md)
2. **深入了解**: 阅读 [README.md](README.md)
3. **准备部署**: 查看 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

祝您交易顺利！🚀

---

**最后更新**: 2026-05-19
**文档版本**: v1.0
