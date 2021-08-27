from flask_mail import Message

class Utilities:
    #   FUNCTION WILL TEST IF GIVEN input IS EMPTY OR NOT
    def not_empty(self, user_input):
        #   IF THE LENGTH ON THE user_input IS 0, THEN THE IT MUST BE EMPTY
        if len(user_input) == 0:
            #   RETURN FALSE IF EMPTY
            raise ValueError
            return False

        #   RETURN TRUE IF NOT EMPTY
        return True

    #   FUNCTION WILL DETERMINE IF user_input IS A VALID EMAIL OR NOT
    def is_email(self, user_input):
        #   .strip() FUNCTION REMOVES EMPTY SPACES BEFORE AND AFTER THE user_input
        email = user_input.strip().lower()
        #   CHECK IF THE email CONTAINS AN @ SYMBOL
        if "@" not in email:
            return False
        #   CHECK IF THE LAST CHARACTERS ARE ONE OF THE OPTIONS
        elif not email[-4:] in [".com", ".org", ".edu", ".gov", ".net"]:
            return False

        #   IF EVERYTHING CHECKS OUT, RETURN True
        return True

    #   FUNCTION WILL SEND AN EMAIL TO THE PROVIDED email_address
    def send_email(self, mail, email_address, first_name):
        email_to_send = Message('Welcome to the Radical Store.', sender='notbrucewayne71@gmail.com',
                                recipients=[email_address])
        email_to_send.body = f"Congratulations {first_name} on a successful registration. \n\n" \
                             f"Welcome to the Radical Store. family, browse around and make sure to enjoy the " \
                             f"experience. "

        mail.send(email_to_send)

    # This function create dictionaries out of SQL rows, so that the data follows JSON format
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

