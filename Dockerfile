FROM python:3.11-slim

# Install build tools and dependencies
RUN apt-get update && apt-get install -y wget unzip

# Download and install portable Chrome to a persistent location
RUN wget -q -O /tmp/chrome-linux.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chrome-linux64.zip \
    && unzip -q /tmp/chrome-linux.zip -d /tmp \
    && mv /tmp/chrome-linux64/chrome /usr/local/bin/chrome \
    && chmod +x /usr/local/bin/chrome

# Verify Chrome installation
RUN /usr/local/bin/chrome --version

# Install specific ChromeDriver version
RUN pip install chromedriver-autoinstaller==0.6.3

# Set up working directory and install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Set environment variable for Chrome
ENV GOOGLE_CHROME_BIN=/usr/local/bin/chrome

# Run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]