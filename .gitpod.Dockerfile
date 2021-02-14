FROM gitpod/workspace-full

USER gitpod

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install -i ~/usr/local/aws-cli -b ~/usr/local/bin && \

RUN echo 'export PATH="~/usr/local/bin:$PATH"' >> ~/.profile
RUN echo 'export PATH="~/usr/local/bin:$PATH"' >> ~/.zshrc

RUN brew update && \
    brew tap aws/tap && \
    brew install aws-sam-cli
