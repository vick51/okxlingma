# 更新日志

## 2026-05-19 - Docker构建优化

### 修复
- ✅ 移除ta-lib依赖，改用pandas原生实现MACD指标
- ✅ 简化Dockerfile，移除TA-Lib原生库编译步骤
- ✅ 更新requirements.txt，使用pandas-ta替代ta-lib
- ✅ 修复ccxt版本问题，改为>=4.0.0

### 改进
- 🚀 Docker构建速度更快（无需编译C扩展）
- 📦 减少Docker镜像大小
- 🔧 提高依赖安装成功率
- 🌐 使用官方PyPI源（移除国内镜像）

### 新增
- 📝 Git自动提交脚本（commit.bat/commit.sh）
- 📋 Git使用指南（GIT_GUIDE.md）
- 🔄 Docker Compose V2支持
- 📄 DOCKER_V2_UPDATE.md 更新说明

### 变更
- 📌 requirements.txt: ta-lib==0.4.28 → pandas-ta>=0.3.14b0
- 📌 ccxt==4.2.0 → ccxt>=4.0.0
- 🐳 Dockerfile: 移除TA-Lib编译步骤
- 🔧 所有docker-compose命令更新为V2格式

---

## 技术说明

### MACD指标实现

之前使用ta-lib库：
```python
import talib
macd, signal, hist = talib.MACD(...)
```

现在使用纯pandas实现：
```python
import pandas as pd
ema_fast = prices.ewm(span=12, adjust=False).mean()
ema_slow = prices.ewm(span=26, adjust=False).mean()
macd_line = ema_fast - ema_slow
signal_line = macd_line.ewm(span=9, adjust=False).mean()
histogram = macd_line - signal_line
```

**优势**:
- ✅ 无需编译C扩展
- ✅ 安装简单快速
- ✅ 跨平台兼容性好
- ✅ 功能完全相同

---

**提交时间**: 2026-05-19  
**版本**: v1.0.1
