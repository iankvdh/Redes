from threading import Thread
from queue import Queue
import socket
import traceback
from lib.transport_protocols.protocol_segment import TransportProtocolSegment



class ServerSender:
    def __init__(self, socket: socket.socket, send_queue: Queue, logger=None):
        self.socket = socket
        self.send_queue = send_queue
        self.logger = logger
        self.running = True

    def run(self):
        try:
            while True:
                segment, address = self.send_queue.get()
                if address == self.socket.getsockname():
                    self.logger.debug("Received FIN segment, stopping sender thread")
                    break
                segment_bytes = segment.to_bytes()
                self.socket.sendto(segment_bytes, address)
                self.logger.debug(f"Sent segment with sequence number {segment.seq_num} to {address}")
        except OSError as e:
            ### ESTE SELF.RUNNING NO SIRVE.
            if self.running:
                self.logger.error(f"Unexpected socket close in Server Sender: {e}")
                traceback.print_exc()
        except Exception as e:
            self.logger.error(f"Unexpected error in Server Sender: {e}")
            traceback.print_exc()

    def close(self):
        self.send_queue.put((TransportProtocolSegment.create_fin(0, 0), (self.socket.getsockname())))
        self.logger.debug("Stopping Server Sender thread")