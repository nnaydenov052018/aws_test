FROM centos:7
RUN yum install -y python3 \
&& pip3 install Gmail-command-line-tool-Nikola-Naydenov --extra-index-url=https://test.pypi.org/simple/
CMD ["/bin/bash"]
