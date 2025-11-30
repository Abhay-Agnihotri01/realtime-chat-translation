# FROM python:3.12-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     git \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Install Node.js
# RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
#     && apt-get install -y nodejs

# # Copy and install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend files
# COPY backend/ ./backend/
# COPY app.py .

# # Copy and build frontend
# COPY frontend/ ./frontend/
# WORKDIR /app/frontend
# RUN npm install && npm run build

# # Move built frontend to serve location
# WORKDIR /app
# RUN cp -r frontend/dist ./static

# # Expose port
# EXPOSE 7860

# # Start the application
# CMD ["python", "app.py"]


# FROM python:3.12-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     git \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy and install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend files
# COPY backend/ ./backend/
# COPY app.py .

# # Copy pre-built frontend (static files)
# COPY static/ ./static/

# # Expose port
# EXPOSE 7860

# # Start the application
# CMD ["python", "app.py"]


FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/
COPY app.py .

# Copy pre-built frontend (static files)
COPY static/ ./static/

# Expose port
EXPOSE 7860

# Start the application
CMD ["python", "app.py"]

