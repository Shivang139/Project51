# Use a slim, official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Expose the Streamlit port AND the health check port
EXPOSE 8501
EXPOSE 8081

# Command to run the Streamlit app.
CMD ["streamlit", "run", "app.py"]