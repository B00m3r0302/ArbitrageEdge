FROM ubuntu:latest
LABEL authors="hudso"

ENTRYPOINT ["top", "-b"]