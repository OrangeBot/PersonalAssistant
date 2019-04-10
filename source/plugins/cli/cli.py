import logging

from pyutils import is_python_3, run_bg

from source.plugins.base import Plugin

if not is_python_3():
    input = raw_input


class CLI(Plugin):
    def setup_callbacks(self):
        self.run_input_listener()

    def populate_schedule(self):
        pass  # no regular tasks

    # --------------------------------------------------------------------------------------------------
    # raw_input_server
    def _run_input_listener(self):
        while self.pa.active:
            command = self.get_input_message()
            self.process_input(command)

    def run_input_listener(self):
        run_bg(self._run_input_listener)

    # --------------------------------------------------------------------------------------------------
    # raw_input_processor

    @staticmethod
    def get_input_message():
        return input("PersonalAssistantCLI:$ ")

    # general logic
    def process_input(self, command):
        logging.info("Received CLI command {}".format(command))
        if command == 'exit':
            self.pa.shutdown()
        elif command == 'help':
            self.display_help()
        else:
            self.display_message("Received unknown command '{}'".format(command))
            self.display_help()

    def display_help(self):
        self.display_message("Supported commands: exit, help")

    def display_message(self, message):
        print(message)
