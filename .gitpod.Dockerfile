FROM gitpod/workspace-full

USER gitpod

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    sudo ./aws/install

RUN brew update && \
    brew tap aws/tap && \
    brew install aws-sam-cli
