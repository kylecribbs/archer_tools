FROM python:3.6-alpine

LABEL description="Archer Tools CLI for multiple things!." \
	maintainer="comm-cso-ceg-cdd-Archer@example.com" \
	source="https://sc.appdev.proj.coe.example.com/ceg/cmd/archer/archer_tools" \
	run="docker run --rm -it archer_tools" \
	classification="UNCLASSIFIED//FOUO"

ADD https://pki.web.org.example.com/content/Assets/apachebundles/Apache_Bundle_US_IC.crt /etc/ssl/certs/ca-bundle.crt
ADD init.sh /init.sh
ADD pip.conf /etc/pip.conf
ADD repositories /etc/apk/repositories


RUN pip install --prefer-binary archer_tools status-client

CMD ["/bin/ash", "-c", "/init.sh"]
