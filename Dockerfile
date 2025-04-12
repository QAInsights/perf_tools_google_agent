FROM python:3.11-slim

# Set working directory
WORKDIR /app

RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    curl \
    gnupg \
    default-jdk \
    maven \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install JMeter
ENV JMETER_VERSION=5.6.3
ENV JMETER_HOME=/opt/apache-jmeter-${JMETER_VERSION}
ENV PATH=$JMETER_HOME/bin:$PATH

RUN wget https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz \
    && tar -xzf apache-jmeter-${JMETER_VERSION}.tgz -C /opt \
    && rm apache-jmeter-${JMETER_VERSION}.tgz


# Copy and install Python requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt # Modify this line (or add if no pip install exists)


# Copy application code
COPY . .

# Update environment variables for the containerized environment
ENV JMETER_HOME=/opt/apache-jmeter-${JMETER_VERSION}
ENV JMETER_BIN=${JMETER_HOME}/bin/jmeter
ENV GATLING_RUNNER=mvn

USER myuser
ENV PORT=8080
ENV PATH="/home/myuser/.local/bin:$PATH"

EXPOSE 8080

CMD ["python", "main.py"]