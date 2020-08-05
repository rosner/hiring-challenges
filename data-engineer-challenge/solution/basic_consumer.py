#!/usr/bin/env python
#
import csv
import datetime
import json

from confluent_kafka import Consumer


def group_by_minute(kafka_consumer, topic):
    """ The boilerplate is pirated from here as a starting point: 
    # https://github.com/confluentinc/examples/blob/5.5.1-post/clients/cloud/python/consumer.py
    """
    consumer.subscribe(topics)
    try:
        ids_for_current_minute = []
        current_datetime = None
    
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # No message available within timeout.
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting for message or event/error in poll()")
                continue
            elif msg.error():
                print('error: {}'.format(msg.error()))
            else:
                msg_payload = json.loads(msg.value())
                timestamp = msg_payload['ts']
                user_id = msg_payload['uid']
                
                # ignore seconds for comparison purposes later
                message_datetime = datetime.datetime.utcfromtimestamp(timestamp).replace(second=0)
            
                # handle first incoming message
                if current_datetime is None:
                    current_datetime = message_datetime

                # a new minute has started
                elif message_datetime > current_datetime:
                    num_users_in_last_minute = len(set(ids_for_current_minute))

                    print(f"{current_datetime}, {num_users_in_last_minute}")

                    current_datetime = message_datetime
                    ids_for_current_minute = []

                ids_for_current_minute.append(user_id)

        num_users_in_last_minute = len(set(ids_for_current_minute))
        print(f"{current_datetime}, {num_users_in_last_minute}")
        
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()

TOPIC = 'doodle-challenge'

if __name__ == '__main__':
    topics = [TOPIC, ]
    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': f'{TOPIC}-group', 
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': 'false'
        }
    consumer = Consumer(config)
    group_by_minute(consumer, topics)