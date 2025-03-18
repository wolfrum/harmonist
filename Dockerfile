# Use an official Python image as base
FROM python:3.13

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first (for efficient caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project to the container
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port Django runs on
EXPOSE 8000

# Run Django server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]

