FROM python:2.7
LABEL maintainer="Gowri Jagadeesh"

# setting current directory as  working directory
COPY ./techtrends /app
WORKDIR /app

# install dependent packages in requirements.txt
RUN pip  install -r ./requirements.txt

# initialize the database with pre-defined posts in init_db.py
RUN python ./init_db.py

# expose application on port 3111
EXPOSE 3111

# command to run on container start
CMD [ "python", "app.py"]