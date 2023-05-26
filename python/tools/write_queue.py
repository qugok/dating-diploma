from lib.queue_client.kafka_queue_client import QueueClient


client = QueueClient()
client.write_to_processor(b'abracadabra')
