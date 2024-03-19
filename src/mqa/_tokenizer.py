from ._asm_types import *


class Tokenizer:
    """
    Tokenizer class, which specializes on working with mainly the individual characters of the source code.
    """

    # opposite brackets
    opposite_brackets = {"[": "]", "{": "}", "(": ")"}

    @staticmethod
    def tokenize(code: str):
        """
        Splits the input code string into a list of tokens, which then can be used to construct a token tree
        :param code: code string
        :return: list of tokens
        """

        # character pointer
        char_ptr = [-1]

        # next char function
        def next_char() -> str | None:
            char_ptr[0] += 1
            if char_ptr[0] >= len(code):
                return None
            return code[char_ptr[0]]

        # token list (not a tree yet)
        token_list: list[Token] = []

        # on which line of the code the pointer is
        line_number = 0

        # if we are inside a comment
        is_commented = False

        # if we are inside a string
        is_string = False
        string_type = ""

        # token string (the accumulative string)
        token_str = ""

        # fetch each character and do some operations
        while (char := next_char()) is not None:
            # if we are inside a comment
            if char == ";":
                is_commented = True
                continue

            # if we hit a newline
            if char == "\n":
                line_number += 1
                is_commented = False
                if token_str != "":
                    token_list.append(Token(token_str, line_number))
                    token_str = ""
                token_list.append(Token("\n", line_number))
                continue

            # skip this part of the code if it's commented
            if is_commented:
                continue

            # if a character is a space or a comma
            if (char == " " or char == ",") and not is_string:
                if token_str != "":
                    token_list.append(Token(token_str, line_number))
                    token_str = ""

            # if a character is a bracket
            elif (char in "[]{}()") and not is_string:
                if token_str != "":
                    token_list.append(Token(token_str, line_number))
                    token_str = ""
                token_list.append(Token(char, line_number))

            # if a character is a quote
            elif char in "\"\'":
                # add quote back, cuz too lazy to redo the compiler and tokens
                token_str += "\""

                if string_type == char or string_type == "":
                    # if there's an escape character before the quote
                    if char_ptr[0] > 0 and code[char_ptr[0]-1] == "\\":
                        continue

                    # if it was already a string, then make it not a string
                    if is_string:
                        string_type = ""
                    else:
                        string_type = char
                    is_string = not is_string

            # otherwise just add it to token string
            else:
                token_str += char

        if token_str != "":
            token_list.append(Token(token_str, line_number))
            token_list.append(Token("\n", line_number))

        # delete the repeating newlines
        pointer = 0
        while pointer < (len(token_list) - 1):
            if token_list[pointer].token == token_list[pointer + 1].token == "\n":
                token_list.pop(pointer)
                pointer -= 1
            pointer += 1

        return token_list

    @staticmethod
    def build_token_tree(token_list: list[Token]):
        """
        Builds a tree of tokens.
        This function is called recursively.
        :param token_list: list of tokens
        :return: hierarchical token structure
        """

        # token tree
        token_tree: TScope = TScope([], BType.MISSING)

        # token pointer
        token_ptr = [-1]

        # token fetching function
        def next_token() -> Token | None:
            token_ptr[0] += 1
            if token_ptr[0] >= len(token_list):
                return None
            return token_list[token_ptr[0]]

        # make a tree
        while (token := next_token()) is not None:
            # if the token is not a bracket => append & continue
            if token.token not in "[]{}()":
                token_tree.body.append(token)
                continue

            # if it's an opening bracket
            if token.token in "[{(":
                # local scope
                scope = []

                # bracket types
                bracket = token.token
                bracket_opposite = Tokenizer.opposite_brackets[bracket]

                # how many brackets are nested in each other
                nesting = 0

                # go through each scope token and do a recursive call when needed
                while (scope_token := next_token()) is not None:
                    if scope_token.token == bracket_opposite and nesting == 0:
                        built_token_tree = Tokenizer.build_token_tree(scope).body
                        match bracket:
                            case "(":
                                token_tree.body.append(TScope(
                                    built_token_tree, BType.ROUND))
                            case "{":
                                token_tree.body.append(TScope(
                                    built_token_tree, BType.CURVED))
                            case "[":
                                token_tree.body.append(TScope(
                                    built_token_tree, BType.SQUARE))
                        break
                    elif scope_token.token == bracket:
                        nesting += 1
                    elif scope_token.token == bracket_opposite:
                        nesting -= 1
                    scope.append(scope_token)
        return token_tree
