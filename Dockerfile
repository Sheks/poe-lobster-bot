FROM alpine:3.8

RUN apk --no-cache add python3 gcc g++ leptonica-dev tzdata libc-dev python3-dev make curl libmagic bash \
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       tesseract-ocr-dev \
                       tesseract-ocr \
                       fribidi-dev && \
    apk add --virtual .build-deps musl-dev

RUN python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
    echo "Europe/Moscow" > /etc/timezone && \
    date && \
    pip3 install -U pip && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi

COPY rus.traineddata /usr/share/tessdata/rus.traineddata
COPY discord.py-master /tmp/discord.py-master
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -e /tmp/discord.py-master
RUN pip3 install -r /tmp/requirements.txt


ADD . /app
WORKDIR /app
ENTRYPOINT ["python3"]
CMD ["launcher.py"]
