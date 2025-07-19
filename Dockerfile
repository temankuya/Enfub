FROM python:3.10-slim


WORKDIR /app


COPY . .

# Install dependensi (pastikan nama file requirements sesuai, req.txt di repo kamu)
RUN pip install --upgrade pip wheel && \
    pip install -r req.txt

# Jalankan program utama (python -m Kymang)
CMD ["python3", "-m", "Kymang"]
