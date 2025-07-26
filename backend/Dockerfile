# Use a specific Python version
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Copy dependency file first to leverage Docker cache
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory content into the container
COPY . .

# Change ownership of all files to the app user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Command to run the application from the flat directory structure
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]