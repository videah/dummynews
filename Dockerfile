FROM python:3.6-alpine

RUN apk update && apk add gcc musl-dev postgresql-dev postgresql-libs
RUN mkdir /dn

# aka cd /dn
WORKDIR /dn

# Add all files to /dn
ADD . /dn/
# Use github instead of ADD . /dn/
# RUN git clone https://github.com/videah/dummynews /dn/

RUN pip install -r requirements.txt
CMD ["python", "app.py"]