# Dockerfile

# --- Stage 1: Base ---
# Start from an official, slim Python 3.9 image.
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# --- Stage 2: Dependencies ---
# Copy *only* the requirements file first.
# This is a cool Docker trick. It caches this layer, so if you
# don't change your requirements, it won't reinstall them every time.
COPY requirements.txt .

# Install the Python libraries
RUN pip install --no-cache-dir --upgrade pip && \
pip install --no-cache-dir -r requirements.txt

# --- Stage 3: Copy Code ---
# Now, copy the rest of your project code into the /app directory
# (It will skip files from .dockerignore)
COPY ./src ./src
COPY ./models ./models

# --- Stage 4: Expose Port ---
# Tell Docker the app will run on port 8000 (inside the container)
# Note: We'll change the uvicorn command to match this
EXPOSE 8000

# --- Stage 5: Run Command ---
# The command to run when the container starts.
# We tell uvicorn to listen on 0.0.0.0 (all IPs) on port 8000.
CMD ["uvicorn", "src.predict_api:app", "--host", "0.0.0.0", "--port", "8000"]