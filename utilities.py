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
