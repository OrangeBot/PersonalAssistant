import argparse
import logging
import os

from source.core.personal_assistant import PersonalAssistant


def main(config_dir, app_data_dir, launch):
    pa = PersonalAssistant(config_dir=config_dir, app_data_dir=app_data_dir)
    if launch:
        pa.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    from secrets import lib_root

    default_config_dir = os.path.join(lib_root, 'config')
    default_app_data_dir = os.path.join(lib_root, 'app_data')
    parser.add_argument("--config-dir", "-c", default=default_config_dir)
    parser.add_argument("--app-data-dir", "-a", default=default_app_data_dir)
    parser.add_argument("--launch", "--run", action="store_true")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    main(config_dir=args.config_dir, app_data_dir=args.app_data_dir, launch=args.launch)

# read plugins data
