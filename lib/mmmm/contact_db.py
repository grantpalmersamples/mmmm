import mysql.connector


class Contact:
    """
    A contact with an ID and usernames for various platforms.
    """

    def __init__(self, id, cursor):
        self.id = id
        self.cursor = cursor

    def get_usernames(self, platform):
        """
        Gets this contact's usernames for the specified platform.
        :param platform: The name of the platform
        :return: A list of usernames
        """
        query = '''
        select `username`
        from `mmmm`.`contact`
        join `%(platform)s` using (`c_id`)
        where `c_id` = '%(id)s'
        '''
        return [item(0) for item in self.cursor.execute(
                query, (platform=platform, id=self.id)))}


class ContactDB:
    """
    A database of contacts.
    """

    def __init__(self, cursor):
        self.cursor = cursor

    def get_usernames(self, platform):
        """
        Gets a list of all stored usernames for the given platform.
        :param platform: The platform to get usernames for
        :return: The list of usernames
        """
        query = '''
        select `username`
        from `mmmm`.`%(platform)s`
        '''
        return [item(0) for item in self.cursor.execute(
                query, (platform=platform,)))]

    def get_contact(self, platform, username):
        """
        Gets a contact based on a platform and username.
        :param platform: The platform for which the username is
        registered
        :param username: The username
        :return: The Contact
        """
        query = '''
        select `c_id`
        from `mmmm`.`%(platform)s`
        where `username` = '%(username)s'
        '''
        return self.cursor.execute(query,
                                   (platform=platform, username=username))(0)

    def get_unrecognized(self, platform, usernames):
        """
        Produces a list of any unrecognized usernames from the given
        list for the given platform.
        :param platform: The platform for which to search usernames
        :param usernames: The usernames to filter from
        :return: A list of unrecognized usernames
        """
        return [username
                for username in usernames
                if username not in self.get_usernames(platform)]

    def __del__(self):
        self.cursor.close()


def build_contact_db(user):
    '''
    Builds a basic contact database.
    :param user: The user connecting to the database
    :return: A ContactDB
    '''
    return ContactDB(
            mysql.connector.connect(user=user, database='mmmm').cursor())
