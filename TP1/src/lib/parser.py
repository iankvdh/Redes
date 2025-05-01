import argparse
import os
import logging

class Parser:
    def __init__(self, description):
        self.parser = argparse.ArgumentParser(description=description)

    def _add_common_flags(self):
        self.parser.add_argument("-v", "--verbose", action="store_true", default=False, help="increase output verbosity")
        self.parser.add_argument("-q", "--quiet", action="store_true", default=False, help="decrease output verbosity")
        self.parser.add_argument("-H", "--host", type=str, default="localhost", help="host server IP address")
        self.parser.add_argument("-p", "--port", type=int, default=8080, help="port server port")

    def _add_name_and_protocol(self):
        self.parser.add_argument("-n", "--name", type=str, default="", help="file name")
        self.parser.add_argument("-r", "--protocol", type=str, choices=["sw", "sr"], default="sw", help="error recovery protocol")

    def _add_upload_args(self):
        self._add_common_flags()
        self._add_name_and_protocol()
        self.parser.add_argument("-s", "--src", default="", help="source file path")

    def _add_download_args(self):
        self._add_common_flags()
        self._add_name_and_protocol()
        self.parser.add_argument("-d", "--dst", default="", help="destination file path")

    def _add_server_args(self):
        self._add_common_flags()
        self._add_name_and_protocol()
        
        default_storage = os.path.join(os.getcwd(), "storage")
        self.parser.add_argument("-s", "--storage", type=str, default=default_storage, help="storage path for received files")


    def _set_debug_level(self, args):
        if args.verbose and args.quiet:
            raise ValueError("Cannot use both verbose and quiet flags at the same time.")
        if args.quiet:
            args.debug_level = logging.INFO
        elif args.verbose:
            args.debug_level = logging.DEBUG
        else:
            args.debug_level = logging.ERROR
        return args

    def parse_args_upload(self):
        self._add_upload_args()
        args = self.parser.parse_args()
        return self._set_debug_level(args)

    def parse_args_download(self):
        self._add_download_args()
        args = self.parser.parse_args()
        return self._set_debug_level(args)
    
    def parse_args_server(self):
        self._add_server_args()
        args = self.parser.parse_args()
        print(args.storage)
        return self._set_debug_level(args)