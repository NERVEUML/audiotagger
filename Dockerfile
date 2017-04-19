FROM python:3
LABEL Description="audiotagger docker image, not worth your time yet"
#http://stackoverflow.com/questions/41083436/how-to-play-sound-in-a-docker-container
#http://stackoverflow.com/questions/28985714/run-apps-using-audio-in-a-docker-container
RUN apt-get update && apt-get install -y libasound-dev vim screen git libgps-dev gpsd

WORKDIR /opt/
RUN git clone https://github.com/ampledata/kiss.git
RUN git clone https://github.com/ampledata/aprs.git 


WORKDIR /opt/audiotagger
COPY ./ /opt/audiotagger

RUN pip install -r requirements.txt
RUN cd direwolf; make clean; make
#CMD ["python", "./gentag.py","ENV"]
