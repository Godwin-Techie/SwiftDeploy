FROM python:3.11-slim
# Create a non-root user
RUN useradd -m appuser
# Set the working directory
WORKDIR /app
# Copy dependency manifest separately to leverage build cache
COPY app/requirements.txt .
# Install dependencies without cache and copy application code after to optimize layer caching
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
# Switch to non-privileged user and run the application
USER appuser
CMD ["python", "main.py"]