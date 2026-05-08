# 默认使用 AWS 公共镜像源，减少本地访问 Docker Hub 超时的概率。
ARG PYTHON_IMAGE=public.ecr.aws/docker/library/python:3.12-slim
FROM ${PYTHON_IMAGE}

# Python 容器运行参数：不写 pyc 文件，并让日志实时输出到控制台。
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 先安装依赖，再复制业务代码，方便 Docker 构建缓存复用。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

# 启动 FastAPI 应用服务。
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
