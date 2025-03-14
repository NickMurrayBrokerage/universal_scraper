FROM python:3.11-slim 
 
# Install build tools and dependencies 
 
# Download and install portable Chrome to a persistent location 
RUN wget -q -O /tmp/chrome-linux.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chrome-linux64.zip \ 
 
# Verify Chrome installation 
RUN /usr/local/bin/chrome --version 
 
# Set up working directory and install Python dependencies 
WORKDIR /app 
COPY requirements.txt . 
RUN pip install -r requirements.txt 
COPY . . 
 
# Set environment variable for Chrome 
ENV GOOGLE_CHROME_BIN=/usr/local/bin/chrome 
 
# Run the app with Gunicorn 
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"] 
