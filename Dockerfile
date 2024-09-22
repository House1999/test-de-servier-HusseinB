#FROM google/cloud-sdk:slim
FROM python:3.9.13-slim

ENV POETRY_HOME="/root/.poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PYTHONPATH=/opt/app

WORKDIR /opt
COPY . /opt

RUN echo -n \
    && apt update \
    && apt -y upgrade \
    && apt -y install \
        curl \
        gpg \
        sudo \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && pip install --upgrade pip

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-interaction --no-ansi

RUN chmod -R 755 /opt


CMD ["poetry", "run", "bash"]
