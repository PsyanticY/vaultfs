# Start from Alpine 3.8 as it container python3.6, which is a requirement.
FROM alpine:3.8

# Add python3 and dependencies.
RUN apk --no-cache add python3 fuse-dev

# Copy all necessary files in a "shadow" hierarchy at /opt/vaultfs
ADD vaultfs/*.py /opt/vaultfs/vaultfs/
ADD LICENSE README.md README.rst requirements.txt setup.py /opt/vaultfs/
ADD config/vaultfs.cfg /opt/vaultfs/config/

# Install to /usr/bin
RUN mkdir -p /local \
    && cd /opt/vaultfs \
    && python3.6 /opt/vaultfs/setup.py install

# Create a volume that will be available to reverse mounting from the outside
# (so other containers can also access it)
VOLUME [ "/vault" ]
WORKDIR /vault

# Default to an internal local caching directory and the exported volume for the
# externally facing mount directory.
ENTRYPOINT [ "/usr/bin/vaultfs" , "-l", "/local", "-m", "/vault" ]
CMD [ "-h" ]