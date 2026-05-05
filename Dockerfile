FROM python:3.11-slim

WORKDIR /app

# Build tools needed to compile pyswisseph from source if no wheel is available
RUN apt-get update && apt-get i