ARG PYTHON_VERSION=3.13.1

FROM python:${PYTHON_VERSION}-slim-bookworm AS python

# $ Stage 1: build dependency wheels
# * Basically python wheels are a precompiled binary package for Python modules than source distributions and they dun require compilation during installation,
# * They are used to install dependencies in a faster and more efficent way
FROM python AS python-build-stage

# ? Run command to execute a command in the container
# ? apt which is package manager for Ubuntu and Debian system
# * `apt-get update` -> updating the package index using APT as the package manager to get latest information about available packages
# * `apt-get install` -> to install packages in the container
RUN apt-get update && apt-get install \
    # ? This will tell apt to only install the required dependencies
    --no-install-recommends -y \
    # ? build-essential is a meta package in Debian and Ubuntu system that installs everythings needed to compile the software
    # * In our case, we need the build essential in our Dockerfile cuz some python packages in our requirements.txt like psycopg, asyncpg pakcages and potentially others are not pure python packages
    # * They contain some C extensions that need to be compiled during installation
    build-essential \
    # ? This is the development package that inclucdes all necessary files for building python packages that need to interact with Postgres like psycopg and asyncpg packages, which are in our requirements.txt file
    libpq-dev

# ? We are going to use this copy files or directories from the host machine to the container
# * We can symbolize the location of the contianer with the dot(.)
COPY ./backend/requirements.txt .

# ? We are goint to create python dependency and sub dependency wheels by using run cmd
RUN pip wheel --wheel-dir /usr/src/app/wheels \
    # ? read the requirements.txt fiel and install dependencies
    -r requirements.txt \
    # ? We are preventing pip from using its cache directory
    # * This is going to help us in reducing the Docker image size
    --no-cache-dir

# $ Stage 2: Python run stage
FROM python AS python-run-stage

ARG APP_HOME=/src
ARG APP_USER=fastapi
ARG APP_GROUP=fastapi

# * By doing that, we are preventing pythong from writing .pyc file which are compiled bytecode files to our disk
# ? This is useful for reducing the size of the final Docker image
ENV PYTHONDONTWRITEBYTECODE=1 \
    # ? Preventing python from buffering the output
    # ? This means that the output will be sent directly to the console or the terminal without any buffering thus allowing some real time output
    PYTHONUNBUFFERED=1

# ? After setting the environment variables, we're going to set the working directory to the application home directory in our container
WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
    sudo git bash-completion nano ssh \
    gettext \
    # ? This command basically removes any unnecessary packages and cleanup the package cache.
    && apt-get purge -y --auto-remove -o APT::AutoRemove:RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*


RUN groupadd -r ${APP_GROUP} && \
    useradd -r -g ${APP_GROUP} -d ${APP_HOME} -m ${APP_USER}

RUN mkdir -p ${APP_HOME}/backend/app/logs && \
    chown -R ${APP_USER}:${APP_GROUP} ${APP_HOME}/backend/app/logs && \
    chmod 775 ${APP_HOME}/backend/app/logs

COPY --from=python-build-stage /usr/src/app/wheels /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/*.whl \
    && rm -rf /wheels/

COPY --chown=${APP_USER}:${APP_GROUP} ./backend/docker/local/fastapi/entrypoint.sh /entrypoint.sh

COPY --chown=${APP_USER}:${APP_GROUP} ./backend/docker/local/fastapi/start.sh /start.sh

RUN sed -i 's/\r$//g' /entrypoint.sh /start.sh && \
    chmod +x /entrypoint.sh /start.sh

COPY --chown=${APP_USER}:${APP_GROUP} . ${APP_HOME}

USER ${APP_USER}

ENTRYPOINT [ "/entrypoint.sh" ]
