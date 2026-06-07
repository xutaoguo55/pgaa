FROM python:3.10-slim

RUN pip install numpy scipy pandas scanpy scikit-learn statsmodels matplotlib
RUN apt-get update && apt-get install -y r-base r-cran-mass

WORKDIR /app
COPY pgaa/ pgaa/
COPY pgaa_r/ pgaa_r/
COPY scripts/ scripts/
COPY requirements.txt .

CMD ["python", "-c", "from pgaa.core.prt import prt_s1_test; print('PGAA ready')"]
