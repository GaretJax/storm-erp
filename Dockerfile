FROM ubuntu:14.04
MAINTAINER Jonathan Stoppani "jonathan@stoppani.name"

# Setup environment
ENV DEBIAN_FRONTEND noninteractive
RUN /usr/sbin/locale-gen en_US.UTF-8 && \
	/usr/sbin/update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Update the system and add additional sources
RUN /usr/bin/apt-get update && \
	/usr/bin/apt-get -y upgrade

# Install dependencies
RUN /usr/bin/apt-get install -y \
	python-dev python-pip \
	postgresql-client-9.3 libpq5 \
	libxml2-dev libxslt1-dev \
	libpq-dev python-dev

# Install requirements here so that we don't have to install them each time
# the app changes
ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

# Add the alembic configuration file (uncomment if needed)
#ADD alembic.ini /etc/alembic.ini

# Install the app
ADD . /src
RUN pip install --no-deps /src/*.whl

# Configure runtime environment
#USER nobody
