from fedora

RUN dnf install python3 -y
RUN pip3 install requests

ADD github_api.py /
ADD thread_github.py /

CMD ["/start.sh"]
