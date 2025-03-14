FROM python:3.11-slim

# Install GPG and add Debian repository keys
RUN apt-get update && apt-get install -y gnupg \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9 6ED0E7B82643E131 605C66F00D6C9793 112695A0E562B32A 54404762BBB6E853

# Install build tools, dependencies, and libraries required by Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    libglib2.0-0 \
    libgtk-3-0 \
    libdbus-1-3 \
    libxt6 \
    x11-utils \
    libx11-6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgbm1 \
    libnss3 \
    libnspr4 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install specific ChromeDriver version
RUN pip install chromedriver-autoinstaller==0.6.3

# Set up working directory and install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Download and install portable Chrome to a persistent location with enhanced debug
RUN echo "Starting Chrome download..." \
    && wget -v -O /tmp/chrome-linux.zip https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.88/linux64/chrome-linux64.zip || { echo "wget failed"; exit 1; } \
    && ls -l /tmp/chrome-linux.zip \
    && mkdir -p /opt/chrome \
    && unzip -q /tmp/chrome-linux.zip -d /opt/chrome || { echo "unzip failed"; exit 1; } \
    && ls -l /opt/chrome/chrome-linux64/ \
    && mv /opt/chrome/chrome-linux64/chrome /usr/local/bin/chrome || { echo "mv failed"; exit 1; } \
    && chmod +x /usr/local/bin/chrome \
    && ls -l /usr/local/bin/chrome \
    && echo "Chrome installation completed"

# Verify Chrome installation
RUN /usr/local/bin/chrome --version

# Set environment variable for Chrome
ENV GOOGLE_CHROME_BIN=/usr/local/bin/chrome

# Create entrypoint script for runtime debug
RUN echo "#!/bin/bash" > /entrypoint.sh \
    && echo "echo 'Checking Chrome binary at runtime...'" >> /entrypoint.sh \
    && echo "ls -l /usr/local/bin/chrome" >> /entrypoint.sh \
    && echo "exec gunicorn --bind 0.0.0.0:\$PORT app:app" >> /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Run the app with Gunicorn using entrypoint for debug
CMD ["/entrypoint.sh"]