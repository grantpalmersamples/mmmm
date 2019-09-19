import json
import logging
import sys
from os import getenv

from mmmm import platforms
from mmmm import basic
from mmmm.contact_db import build_contact_db


class CLI(basic.CLI):
    """
    The main utility for a command line interface for templated
    mass-messaging, capable of fully processing all external resources
    used by the script.
    """

    def __init__(self):
        super().__init__()
        self.add_data_arg()
        self.add_db_username_arg()

    def add_data_arg(self):
        self.add_argument(
            'data',
            help='The JSON data used for filling the content template',
            nargs='?'
        )

    def add_db_username_arg(self):
        self.add_argument(
            '--db-username',
            help='The username for the user accessing the contact database'
        )

    def add_recipients_arg(self):
        self.add_argument(
            '-r',
            '--recipients',
            help='List of recipients to send to',
            nargs='*',
            default=[]
        )

    @classmethod
    def fill_in_args(cls,
                     platform_name,
                     sender_json,
                     recipients_text,
                     content,
                     templating_data_json,
                     db_username
                     ):
        """
        Attempts to fill in null command line arguments.
        :param platform_name: The name of the platform over which to
        send messages
        :param sender_json: The platform-specific JSON data
        representing the sender
        :param recipients_text: A list of platform-specific textual
        representations of recipients
        :param content: The template for the content of the messages
        :param templating_data_json: JSON representing the full set of
        data used to fill the template
        :param db_username: The username for the user accessing the
        contact database
        :return: A dictionary of the key value pairs reflecting the
        arguments to this function after attempting to fill in null
        values
        """
        if templating_data_json is None:
            logging.debug('Data not specified in command line args. Reading '
                          'from stdin.')
            templating_data_json = sys.stdin.read()
        if db_username is None:
            logging.debug('Database username not specified in command line'
                          'args. Attempting to load from environment '
                          'variables.')
            db_username = getenv('mmmm_db_user'.upper())
            if db_username is None:
                raise ValueError('No username specified for the contact'
                                 'database. Please specify via the command '
                                 'line or the MMMM_DB_USER environment '
                                 'variable.')
        return {
            **super().fill_in_args(platform_name,
                                   sender_json,
                                   recipients_text,
                                   content),
            'templating_data_json': templating_data_json,
            'db_username': db_username
        }

    @classmethod
    def parse_to_python(cls,
                        platform_name,
                        sender_json,
                        recipients_text,
                        content,
                        templating_data_json,
                        db_username):
        """
        Parses raw arguments (as from the command line) into
        program-agnostic data representations.  Returns the following:
        - platform_name: The name of the platform over which to send
          messages
        - sender_data: A platform-specific dictionary representing the
          sender
        - recipients_data: A list of platform-specific representations
          of recipients
        - content: The template for the content of the messages
        - templating_data: The full set of data used to fill the
          template
        - db_username The username for the user accessing the contact
          database
        :param platform_name: The name of the platform over which to
        send messages
        :param sender_json: The platform-specific JSON data
        representing the sender
        :param recipients_text: A list of platform-specific textual
        representations of recipients
        :param content: The template for the content of the messages
        :param templating_data_json: JSON representing the full set of
        data used to fill the template
        :param db_username: The username for the user accessing the
        contact database
        :return: A dictionary containing the key value pairs described
        above
        """
        templating_data = json.loads(templating_data_json)
        return {
            **super().parse_to_python(platform_name,
                                      sender_json,
                                      recipients_text,
                                      content),
            'templating_data': templating_data,
            'db_username': db_username
        }

    def get_args(self):
        """
        Loads and processes all external resources used by the script.
        The resources are as follows:
        - platform_name: The name of the platform over which to send
          messages
        - sender_data: A platform-specific dictionary representing
          the sender
        - recipients_data: A list of platform-specific
          representations of recipients
        - content: The template for the content of the messages
        - templating_data: The full set of data used to fill the
          template
        - db_username: The username for the user accessing the
          contact database
        :return: A dictionary containing the key value pairs described
        above
        """
        args = self.parse_args()
        return self.parse_to_python(**self.fill_in_args(args.platform,
                                                        args.sender,
                                                        args.recipients,
                                                        args.content,
                                                        args.data,
                                                        args.db_username))


def build_resources(platform_name,
                    sender_data,
                    recipients_data,
                    content,
                    templating_data,
                    db_username):
    """
    Parses program-agnostic data representations into
    platform-specific classes.  The resources are as follows:
    - platform: An instance of the `mmmm.platform.Platform`
      subclass corresponding to the given platform name
    - sender: An instance of the `mmmm.platform.ClientUser`
      subclass corresponding to the given platform name
    - recipients: A list of instances of the `mmmm.platform.User`
      subclass corresponding to the given platform name
    - content: The template for the content of the messages
    - templating_data: The full set of data used to fill the
      template
    - contact_db: An instance of `mmmm.contact_db.ContactDB`
    :param platform_name: The name of the platform over which to
    send messages
    :param sender_data: A platform-specific dictionary representing
    the sender
    :param recipients_data: A list of platform-specific
    representations of recipients
    :param content: The template for the content of the messages
    :param templating_data: The full set of data used to fill the
    template
    :param db_username: The username for the user accessing the
    contact database
    :return: A dictionary containing the key value pairs described
    above
    """
    contact_db = build_contact_db(db_username)
    if recipients_data == []:
        logging.debug('No recipients specified in command line args. '
                      'Loading recipients from user table.')
        recipients_data = [*contact_db.get_usernames(platform_name)]
    return {
        **basic.build_resources(platform_name,
                                sender_data,
                                recipients_data,
                                content),
        'templating_data': templating_data,
        'contact_db': contact_db
    }


def build_messages(platform,
                   sender,
                   recipients,
                   content,
                   templating_data,
                   contact_db,
                   template_input_builder):
    """
    Produces a list of messages with the same sender.  The content is
    a template filled with personalized data for each recipient.
    No message will be produced for recipients with no corresponding
    data.
    :param platform: An instance of the `mmmm.platform.Platform`
    subclass corresponding to the platform over which the message will
    be sent
    :param sender: An instance of the `mmmm.platform.ClientUser`
    subclass corresponding to the platform over which the message will
    be sent
    :param recipients: A list of instances of the `mmmm.platform.User`
    subclass corresponding to the platform over which the message will
    be sent
    :param content: The template for the content of the messages
    :param templating_data: The full set of data used to fill the
    template
    :param contact_db: An instance of `mmmm.contact_db.ContactDB`
    :param template_input_builder: A function that returns the strings
    used to fill the message content template with personalized
    information from provided data, or returns None if no relevant
    information is found
    :return: A list of `mmmm.basic.Message` objects
    """
    platform_name = platforms.platform_name[type(platform)]
    unfilled_messages = basic.build_messages(sender, recipients, content)
    messages = []
    for message in unfilled_messages:
        recipient_id = message.recipient.get_id()
        try:
            user = contact_db.get_contact(platform_name, recipient_id)
        except KeyError:
            logging.error('Skipping user \'{}\' because no user table entry '
                          'was found'.format(recipient_id))
            continue
        template_input = template_input_builder(user=user,
                                                data=templating_data)
        if template_input is None:
            continue
        try:
            content = message.content.format(*template_input)
        except TypeError as e:
            raise TypeError('Output of template_input_builder must be a '
                            'tuple.') from e
        messages.append(basic.Message(message.sender,
                                      message.recipient,
                                      content))
    return messages


def _send_to_all(platform,
                 sender,
                 recipients,
                 content,
                 templating_data,
                 contact_db,
                 template_input_builder):
    """
    Requires instances of platform-specific classes; for internal use.
    """
    messages = build_messages(**locals())
    for message in messages:
        basic.send_message(message)


def send_to_all(platform_name,
                sender_data,
                recipients_data,
                content,
                templating_data,
                db_username,
                template_input_builder):
    """
    Formats a message template for a set of recipients with
    personalized information pulled from the given data, then sends
    the messages via the specified platform. Messages are only sent to
    recipients for which corresponding information can be found.
    :param platform_name: The name of the platform over which to send
    messages
    :param sender_data: A platform-specific dictionary representing
    the sender
    :param recipients_data: A list of platform-specific
    representations of recipients
    :param content: The template for the content of the messages
    :param templating_data: The full set of data used to fill the
    template
    :param db_username: The username for the user accessing the
    contact database
    :param template_input_builder: A function that returns the strings
    used to fill the message content template with personalized
    information from provided data, or returns None if no relevant
    information is found
    """
    _send_to_all(template_input_builder=template_input_builder,
                 **build_resources(platform_name,
                                   sender_data,
                                   recipients_data,
                                   content,
                                   templating_data,
                                   db_username))
