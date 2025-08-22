# 新发地价格数据抓取系统

一个用于抓取新发地农产品价格数据的Python系统，支持数据存储、API接口和自动化管理。

## 功能特性

- 🚀 **高效抓取**: 支持多页数据抓取，内置速率限制防止429错误
- 🗄️ **数据管理**: 使用SQLAlchemy + MySQL存储，支持去重和增量同步
- 🔌 **API接口**: 提供完整的RESTful API，支持CRUD操作
- 📊 **统计分析**: 内置数据统计和分析功能
- 🛠️ **命令行工具**: 支持命令行操作，方便自动化部署
- 📝 **日志记录**: 完整的日志系统，支持多级别日志输出

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd price-data

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接：

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/price_data
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 3. 初始化数据库

```bash
# 初始化数据库表
python main.py init
```

### 4. 数据同步

```bash
# 同步最新数据（默认20条/页）
python main.py sync

# 同步更多数据
python main.py sync --limit 50 --max-pages 10

# 增量同步最近3天的数据
python main.py sync --incremental --days 3

# 同步特定产品
python main.py sync --product "白菜"
```

### 5. 启动API服务

```bash
# 启动生产服务器
python main.py server

# 启动开发服务器（支持热重载）
python main.py server --reload

# 自定义端口
python main.py server --port 9000
```

## API 文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

#### 价格数据

- `GET /api/prices` - 获取价格数据列表
- `GET /api/prices/{id}` - 获取单个价格数据
- `POST /api/prices` - 创建价格数据
- `PUT /api/prices/{id}` - 更新价格数据
- `DELETE /api/prices/{id}` - 删除价格数据

#### 数据同步

- `POST /api/sync` - 同步数据
- `POST /api/sync/incremental` - 增量同步
- `GET /api/sync/status` - 获取同步状态

#### 统计信息

- `GET /api/statistics` - 获取数据统计
- `GET /api/products` - 获取产品列表
- `GET /api/categories` - 获取分类列表

#### 数据管理

- `GET /api/duplicates` - 获取重复记录
- `POST /api/duplicates/clean` - 清理重复记录
- `GET /api/logs` - 获取抓取日志

### API 使用示例

#### 获取价格数据

```bash
# 获取最新20条数据
curl "http://localhost:8000/api/prices"

# 按产品名称搜索
curl "http://localhost:8000/api/prices?prod_name=白菜"

# 按日期范围查询
curl "http://localhost:8000/api/prices?date_from=2024-01-01&date_to=2024-01-31"

# 按价格范围查询
curl "http://localhost:8000/api/prices?min_price=1.0&max_price=10.0"
```

#### 同步数据

```bash
# 同步数据
curl -X POST "http://localhost:8000/api/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 50,
    "max_pages": 5
  }'

# 增量同步
curl -X POST "http://localhost:8000/api/sync/incremental?days=1"
```

#### 获取统计信息

```bash
# 获取数据统计
curl "http://localhost:8000/api/statistics"

# 获取同步状态
curl "http://localhost:8000/api/sync/status"
```

## 命令行工具

### 数据同步

```bash
# 基本同步
python main.py sync

# 高级同步选项
python main.py sync --limit 100 --max-pages 20
python main.py sync --product "苹果" --category "1186"
python main.py sync --incremental --days 7
```

### 系统状态

```bash
# 检查系统状态
python main.py status

# 详细状态信息
python main.py status --verbose
```

### 数据清理

```bash
# 清理重复记录
python main.py clean --duplicates

# 保留最旧的记录
python main.py clean --duplicates --keep-oldest
```

### 服务器管理

```bash
# 启动服务器
python main.py server

# 开发模式
python main.py server --reload --log-level debug

# 自定义配置
python main.py server --host 127.0.0.1 --port 9000
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接URL | 必须配置 |
| `API_HOST` | API服务器地址 | `0.0.0.0` |
| `API_PORT` | API服务器端口 | `8000` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

### 配置文件 (config.py)

主要配置项：

- **数据库配置**: 连接URL、连接池设置
- **API配置**: 请求头、超时设置、速率限制
- **日志配置**: 日志级别、输出格式
- **抓取配置**: 默认参数、重试设置

## 数据模型

### PriceData (价格数据)

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `prod_name` | String | 产品名称 |
| `prod_catid` | Integer | 产品分类ID |
| `prod_cat` | String | 产品分类名称 |
| `prod_pcatid` | Integer | 父分类ID |
| `prod_pcat` | String | 父分类名称 |
| `low_price` | Float | 最低价格 |
| `high_price` | Float | 最高价格 |
| `avg_price` | Float | 平均价格 |
| `place` | String | 产地 |
| `spec_info` | String | 规格信息 |
| `unit_info` | String | 单位信息 |
| `pub_date` | DateTime | 发布日期 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

### ScrapingLog (抓取日志)

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `scrape_date` | DateTime | 抓取时间 |
| `total_records` | Integer | 总记录数 |
| `new_records` | Integer | 新增记录数 |
| `updated_records` | Integer | 更新记录数 |
| `status` | String | 状态 |
| `error_message` | Text | 错误信息 |
| `duration` | Float | 执行时长 |

## 部署指南

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py", "server"]
```

```bash
# 构建镜像
docker build -t price-data .

# 运行容器
docker run -d -p 8000:8000 --env-file .env price-data
```

### 系统服务

创建 systemd 服务文件 `/etc/systemd/system/price-data.service`：

```ini
[Unit]
Description=Price Data Scraping Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/price-data
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py server
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl enable price-data
sudo systemctl start price-data
```

### 定时任务

设置 crontab 定时同步数据：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每小时同步一次）
0 * * * * cd /path/to/price-data && python main.py sync --incremental --days 1

# 每天凌晨清理重复数据
0 2 * * * cd /path/to/price-data && python main.py clean --duplicates
```

## 监控和维护

### 日志文件

- `logs/app_YYYY-MM-DD.log` - 应用日志
- `logs/error_YYYY-MM-DD.log` - 错误日志
- `logs/scraping_YYYY-MM-DD.log` - 抓取日志

### 健康检查

```bash
# API健康检查
curl http://localhost:8000/health

# 系统状态检查
python main.py status
```

### 性能优化

1. **数据库优化**:
   - 为常用查询字段添加索引
   - 定期清理过期数据
   - 优化查询语句

2. **抓取优化**:
   - 调整速率限制参数
   - 使用增量同步减少数据传输
   - 合理设置页面大小

3. **API优化**:
   - 启用响应缓存
   - 使用分页减少单次查询数据量
   - 添加请求限流

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证连接字符串格式
   - 确认用户权限

2. **抓取失败**
   - 检查网络连接
   - 验证目标网站是否可访问
   - 调整速率限制参数

3. **API服务无法启动**
   - 检查端口是否被占用
   - 验证依赖包是否正确安装
   - 查看错误日志

### 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python main.py sync

# 或者直接在命令中指定
python main.py server --log-level debug
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持新发地价格数据抓取
- 提供完整的API接口
- 支持命令行操作
- 内置数据去重和同步功能