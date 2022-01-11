FROM rabbitmq:3.8.17

# Define environment variables.
ENV RABBITMQ_USER idss 
ENV RABBITMQ_PASSWORD idss

ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

ADD init.sh /init.sh
RUN chmod +x /init.sh

EXPOSE 15672

RUN rabbitmq-plugins enable --offline rabbitmq_management

# Define default command
CMD [ "/init.sh" ]
