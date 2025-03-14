FROM python:3.11-slim

# Install GPG and add Debian repository keys
RUN apt-get update && apt-get install -y gnupg \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9 6ED0E7B82643E131 605C66F00D6C9793 112695A0E562B32A 54404762BBB6E853

# Install build tools, dependencies, and libraries required by Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libgtk-3-0 \
    libdbus-1-3 \
    libxt6 \
    x11-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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