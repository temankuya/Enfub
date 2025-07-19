FROM python:3.10-slim

# Install dependencies (termasuk ffmpeg)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy semua file dari repo ke container
COPY . .

# Install python dependencies
RUN pip install --upgrade pip wheel
RUN pip install --no-cache-dir -r req.txt

# Jalankan bot
CMD ["python3", "-m", "Kymang"]
