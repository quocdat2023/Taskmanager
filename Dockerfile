# Sử dụng Python 3.10 slim để dung lượng nhẹ
FROM python:3.10-slim

# Thiết lập các biến môi trường
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=run.py
ENV FLASK_CONFIG=production
ENV PORT=7860

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Tạo thư mục uploads và cấp quyền (Hugging Face chạy với user không root)
RUN mkdir -p uploads instance && chmod -R 777 uploads instance

# Hugging Face Spaces yêu cầu expose port 7860 mặc định
EXPOSE 7860

# Lệnh chạy ứng dụng
CMD ["python", "run.py"]
