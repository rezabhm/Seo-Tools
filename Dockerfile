# Base image
FROM python

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Give execution permission to entrypoint
RUN chmod +x entrypoint.sh

# Run entrypoint as default command
CMD ["./entrypoint.sh"]