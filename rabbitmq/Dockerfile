FROM rabbitmq:3.8.17

# Arguments defined in .env file and passed in from command line or compose build
ARG maintainer
ARG rmq_username
ARG rmq_password

LABEL maintainer="${maintainer}"

# Define environment variables.
ENV RABBITMQ_USER "${rmq_username}"
ENV RABBITMQ_PASSWORD "${rmq_password}"

ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

ADD ./init.sh /init.sh
RUN chmod +x /init.sh

EXPOSE 15672

RUN rabbitmq-plugins enable --offline rabbitmq_management

# Define default command
CMD [ "/init.sh" ]
