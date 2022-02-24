import re, itertools

# Part 1 : Classes and functions you must implement - refer to the jupyter notebook
# You may need to write more classes, which can be done here or in separate files, you choose.

# Define global constants
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Rotor name : (mapping order corresponding to alphabet, rotor notch position)
# reflectors don't rotate -> A, B & C have no notches
ROTOR_BOX = {
    "I": ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", 'Q'),
    "II": ("AJDKSIRUXBLHWTMCQGZNPYFVOE", 'E'),
    "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", 'V'),
    "IV": ("ESOVPZJAYQUIRHXLNFTGKDCMWB", 'J'),
    "V": ("VZBRGITYUPSDNHLXAWMJQOFECK", 'Z'),
    "Beta": ("LEYJVCNIXWPBQMDRTAKZGFUHOS", None),
    "Gamma": ("FSOKANUERHMBTIYCWLQPZXVGJD", None),
    "A": ("EJMZALYXVBWFCRQUONTSPIKHGD", None),
    "B": ("YRUHQSLDPXNGOKMIEBFZCWVJAT", None),
    "C": ("FVPJIAOYEDRZXWGCTKUQSBNMHL", None)
}

class PlugLead:
    def __init__(self, mapping: str) -> None:

        # Raise error if mapping is not a string
        if type(mapping) != str: raise TypeError(mapping)

        # Raise error if the mapping is not of length two
        if len(mapping) != 2: raise ValueError(mapping)

        # Raise error if the pluglead connects two of the same characters, e.g 'AA'
        if mapping[0] == mapping[1]: raise ValueError(mapping)

        # Else: is a valid mapping -> store as a tuple
        self.mapping = tuple(mapping)        

    def encode(self, character: str) -> str:
        
        # Unpack mapping into two variables
        pin1, pin2 = self.mapping

        # If character maps to one of the pair, return the other in the pair.
        if pin1 == character: return pin2
        if pin2 == character: return pin1

        # If it is neither, return the character
        return character


class Plugboard:
    def __init__(self) -> None:
        # mapping (a,b) maps a -> b and b -> a in the dictionary, bi-directional link. 
        self.connections = dict()
    
    # Method adds a plug lead to the plug board
    def add(self, newPlugLead: object) -> None:

        # If all the 10 provided wires have been added -> don't add
        if len(self.connections) == 20: raise ValueError

        # Unpack mapping into two variables
        pin1, pin2 = newPlugLead.mapping

        # If either of the characters are already wired -> raise error
        if pin1 in self.connections or pin2 in self.connections: raise ValueError

        # for mapping (a,b):
        self.connections[pin1] = pin2 # maps a -> b 
        self.connections[pin2] = pin1 # maps b -> a

    def remove(self, plugLead: object):

        # Assume pluglead exists
        pin1, pin2 = plugLead.mapping

        # Delete connection
        del self.connections[pin1], self.connections[pin2]

    def encode(self, character):

        # if connection exists, return character it is wired to
        if character in self.connections: return self.connections[character]

        # otherwise just return the character
        return character


class Rotor:
    def __init__(self, rotor_name, rotor_mapping, rotor_notch_position):

        # Define default attributes from rotor_name
        self.name = rotor_name
        self.mapping = rotor_mapping
        self.notch_position = rotor_notch_position

        # Declare custom attributes
        self.position = "A"
        self.ring_setting = 0

    def encode_right_to_left(self, character):
        """
        Alphabet |-> Mapping
        """
        # 1. Find the position of the character in the alphabet
        alphabet_index = ALPHABET.index(character)

        # 2. Find the no. places the rotor has been shifted
        offset = ALPHABET.index(self.position) - self.ring_setting       

        # 3. Get the index of the current pin
        pin_index = (alphabet_index + offset) % 26

        # 4. Find the contact of the current rotor 
        current_contact = self.mapping[pin_index]

        # 5. Translate the contact back to the correct pin for the next rotor
        next_contact_index = (ALPHABET.index(current_contact) - offset) % 26

        # 6. Return the contact for the next rotor
        return ALPHABET[next_contact_index]

    def encode_left_to_right(self, character):
        """
        Mapping |-> Alphabet
        """
        # 1. Find the position of the current character in the alphabet
        alphabet_index = ALPHABET.index(character)

        #2. Find the no. places the rotor has been shifted
        offset = ALPHABET.index(self.position) - self.ring_setting

        # 3. Get the index of the current contact
        contact_index = (alphabet_index + offset) % 26

        # 4. Find the pin for the current rotor's contact
        current_pin = ALPHABET[contact_index]

        # 5. Translate the pin back to the correct pin for the next rotor
        next_pin_index = (self.mapping.index(current_pin) - offset) % 26

        # 6. Return the pin for the next rotor
        return ALPHABET[next_pin_index]

    def rotate(self) -> bool:
        """
        Updates the position of a rotor after rotation. If the last position  a notch, function returns True.
        """
        # Create a variable to remember whether the last position was a notch
        notch_was_rotated = self.position == self.notch_position

        # move the rotor one position up | if this is the last position-> loop back to 0
        alphabet_index = (ALPHABET.index(self.position) + 1) % 26
        
        # Update the new position after rotation
        self.position = ALPHABET[alphabet_index]

        # Indicate whether the notch has been rotated
        return notch_was_rotated


def rotor_from_name(rotor_name: str) -> object:
    """
    Method which returns a Rotor object the given name of the Rotor e.g. I or Gamma.
    """
    # Get row data for a rotor name
    rotor_mapping, rotor_notch_position = ROTOR_BOX[rotor_name]

    # Return the resulting rotor object
    return Rotor(rotor_name, rotor_mapping, rotor_notch_position)


class EnigmaMachine:
    def __init__(self, enigma_rotors: list, enigma_reflector: object, enigma_plugboard: object) -> None:
        self.rotors = enigma_rotors
        self.reflector = enigma_reflector
        self.plugboard = enigma_plugboard

    def encode(self, plaintext):

        ciphertext = ''
        for char in plaintext:

            # 1. Input plugboard encrypted character
            encrypted_char = self.plugboard.encode(char)

            # 2. Rotate rightmost rotor
            i = len(self.rotors) - 1
            current_rotor = self.rotors[i]
            rotor_was_on_notch = current_rotor.rotate()

            # 3. If current rotor is on notch -> rotate inner rotor
            while i != 0 and rotor_was_on_notch:
                i -= 1
                current_rotor = self.rotors[i]
                rotor_was_on_notch = current_rotor.rotate()

            # 4. Signal is passed through rightmost -> leftmost rotor
            for rotor in self.rotors[::-1]:

                # rotor receives signal on X1 pin and connects to Y1 contact
                encrypted_char = rotor.encode_right_to_left(encrypted_char)

            # 5. Leftmost rotor passes signal to reflector
            encrypted_char = self.reflector.encode_right_to_left(encrypted_char)

            # 6. Signal is passed back from leftmost -> rightmost rotor.
            for rotor in self.rotors:

                # rotor receives signal on Y2 contact and connects to X2 pin
                encrypted_char = rotor.encode_left_to_right(encrypted_char)

            # 7. Output plugboard encyption
            encrypted_char = self.plugboard.encode(encrypted_char)

            # 8. Add encoded character to ciphertext
            ciphertext += encrypted_char

        return ciphertext
            

def create_enigma_machine(names_of_rotors: list, reflector_name: str, ring_settings: str, initial_positions: str, plugboard_pairs: list = []) -> object:
    
    # Convert ring settings into a list of ints. '01 02 03' -> [0, 1, 2]
    ring_settings = list(map(
        lambda ring_setting: int(ring_setting) - 1 , ring_settings.split(" ")
    ))

    # Convert initial_positions and rotor_names into lists of strings
    initial_positions = initial_positions.split(" ")
    names_of_rotors = names_of_rotors.split(" ")

    # Create every Rotor object.
    rotors = []
    for rotor_idx in range(len(names_of_rotors)):

        # Create a rotor object from its name
        new_rotor = rotor_from_name(names_of_rotors[rotor_idx])

        # Assign the rotor's ring_setting and initial_position
        new_rotor.ring_setting = ring_settings[rotor_idx]
        new_rotor.position = initial_positions[rotor_idx]

        # Add new rotor object
        rotors.append(new_rotor)

    # Create the reflector
    reflector = rotor_from_name(reflector_name)

    # Create the plugboard object
    plugboard = Plugboard()
    for pluglead_pair in plugboard_pairs:

        try:
            # Create the pluglead
            pluglead = PlugLead(pluglead_pair)

            try:
                # Add pluglead to plugboard
                plugboard.add(pluglead)

            except ValueError: print("Maximum amount of plugleads added. Plugboard only comes with 10 leads.")
        except ValueError: print("Pluglead pair string must be of length 2 consisting of two different letters.")
        except TypeError: print("Pluglead mapping must be a string: e.g. 'ab'")

    return EnigmaMachine(rotors, reflector, plugboard)

# # Part 2 : functions to implement to demonstrate code breaking.
# # each function should return a list of all the possible answers
# # code_one provides an example of how you might declare variables and the return type


def code_one():

    # Define code we're looking at and crib included
    code = "DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ"
    crib = "SECRETS"

    # Define known enigma settings
    rotors = "Beta Gamma V"
    ring_settings = "04 02 14"
    initial_positions = "M J M"
    plugboard = ["KI", "FL", "XN"]

    # Possible messages - if crib is in encoded list
    possible_messages = []

    # Try all reflectors in the enigma machine
    for reflector in ["A", "B", "C"]:
        enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, plugboard)
        possible_message = enigma.encode(code)

        if crib in possible_message:
            possible_messages.append(possible_message)

    return possible_messages


def code_two():

    # Define code we're looking at and crib included
    code = "CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH"
    crib = "UNIVERSITY"

    # Define known enigma settings
    rotors = "Beta I III"
    reflector = "B"
    ring_settings = "23 02 10"
    plugboard = ["VH", "PT", "ZG", "BJ", "EY", "FS"]

    # Possible messages - if crib is in encoded list
    possible_messages = []

    # Try all combos of P1 P2 P3 [1-26] (inclusive)
    for p1 in range(26):
        for p2 in range(26):
            for p3 in range(26):

                # create initial position from p1, p2, p3
                initial_positions = ALPHABET[p1] + " " + ALPHABET[p2] + " " + ALPHABET[p3]

                # create enigma based off 
                enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, plugboard)
                possible_message = enigma.encode(code)

                # check if crib in message
                if crib in possible_message:
                    possible_messages.append(possible_message)

    return possible_messages


def code_three():

    # Define code we're looking at and crib included
    code = "ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY"
    crib = "THOUSANDS"

    # Possible messages - if crib is in encoded list
    possible_messages = []

    # Define known enigma settings
    initial_positions = "E M Y"
    plugboard_pairs = ["FH", "TS", "BE", "UQ", "KD", "AL"]
    
    # All ring settings without an odd integer
    possible_ring_setting = ['02', '04', '06', '08', '20', '22', '24', '26']

    # Possible rotors -> only even and letters
    rotor_choices = ['II', 'IV', 'Beta', 'Gamma']

    combinations_of_rotors = [" ".join([r1, r2, r3]) for r1 in rotor_choices for r2 in rotor_choices for r3 in rotor_choices]

    # Try every combination of rotor
    for rotors in combinations_of_rotors:

        # Try every reflector
        for reflector in ["A", "B", "C"]:

            # Try all combos of P1 P2 P3 [1-26] (inclusive)
            for p1 in possible_ring_setting:
                for p2 in possible_ring_setting:
                    for p3 in possible_ring_setting:

                        # create initial position from p1, p2, p3
                        ring_settings = p1 + " " + p2 + " " + p3

                        # create enigma based off 
                        enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, plugboard_pairs)
                        possible_message = enigma.encode(code)

                        # check if crib in message
                        if crib in possible_message:
                            possible_messages.append(possible_message)
    
    return possible_messages


def code_four():

    # Define code we're looking at and crib included
    code = "SDNTVTPHRBNWTLMZTQKZGADDQYPFNHBPNHCQGBGMZPZLUAVGDQVYRBFYYEIXQWVTHXGNW"
    crib = "TUTOR"

    # Possible messages - if crib is in encoded list
    possible_messages = []

    # Define known settings of enigma machine
    rotors = "V III IV"
    reflector = "A"
    ring_settings = "24 12 10"
    initial_positions = "S W U"

    # Define known and unknown pairs
    pluglead_pairs = ["WP", "RJ", "VF", "HN", "CG", "BS"]
    unknown_connections = ["A", "I"]

    # Create a list of possible connections for 'A' and 'I'
    possible_letters_for_a = []
    for letter in ALPHABET:

        # possible connections for A and I are those not already plugged in
        if letter not in unknown_connections and letter not in "".join(pluglead_pairs):
            possible_letters_for_a.append(letter)
    
    # Try possible connections for the unknknown side of the pair [A?, I?] 
    for unknown_side in possible_letters_for_a:

        # Add connection to end of plugboard pairs
        possible_pair = "A" + unknown_side
        pluglead_pairs.append(possible_pair)

        # Remove used connection before trying again
        possible_letters_for_i = possible_letters_for_a.copy()
        possible_letters_for_i.remove(unknown_side)

        for unknown_side in possible_letters_for_i:

            # Add connection to end of plugboard pairs
            possible_pair = "I" + unknown_side
            pluglead_pairs.append(possible_pair)

            # Try enigma machine
            enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, pluglead_pairs)
            possible_message = enigma.encode(code)

            # check if crib in message
            if crib in possible_message:
                possible_messages.append(possible_message)

            pluglead_pairs.pop()

        pluglead_pairs.pop()

    return possible_messages



def code_five():

    # Define code we're looking at and crib included
    code = "HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX"
    cribs = ["INSTAGRAM", "FACEBOOK", "TWITTER"]

    # Possible messages - if crib is in encoded list
    possible_messages = []

    # Define known engigma attributes / settings
    rotors = "V II IV"
    ring_settings = "06 18 07"
    initial_positions = "A J L"
    plugboard_pairs = ["UG", "IE", "PO", "NX", "WT"]

    for reflector_name in ["A", "B", "C"]:

        # 1. Create all pairs in reflector
        original_reflector = rotor_from_name(reflector_name)
        original_pairs = set()

        for letter in ALPHABET:

            # Create pair as a set so order doesn't matter {a, b} = {b, a}
            pair = frozenset([letter, original_reflector.encode_right_to_left(letter)])

            # if {b, a} not in pairs, add (a, b)
            if pair not in original_pairs:
                original_pairs.add(tuple(pair))

        # 2. Get every combination of choosing 4 pairs out of 13
        chosen_pairs_list = list(itertools.combinations(original_pairs, 4))

        for chosen_pairs in chosen_pairs_list:

            # Get every order of the 4 chosen pairs
            combinations_of_wire_pairings = [

                # pair of wires 1
                ((chosen_pairs[i], chosen_pairs[j]),

                # pair of wires 2
                tuple([x for idx, x in enumerate(chosen_pairs) if idx not in (i, j)]))

                for i in range(len(chosen_pairs)) for j in range(i + 1, len(chosen_pairs))
            ]

            # Swap the wires for every order of pairs
            for combination_of_wires in combinations_of_wire_pairings:
                
                # Now swap wirings
                (pairA, pairB), (pairX, pairY) = combination_of_wires

                # Unwire wires A and B
                a1, a2 = pairA
                b1, b2 = pairB

                # Unwire wires X and Y
                x1, x2 = pairX
                y1, y2 = pairY

                # 4 ways to swap pair wirings
                swapped_pairs_configurations = [
                    [(a1, b1), (a2, b2), (x1, y1), (x2, y2)], # 1
                    [(a1, b1), (a2, b2), (x1, y2), (x2, y1)], # 2
                    [(a1, b2), (a2, b1), (x1, y1), (x2, y2)], # 3
                    [(a1, b2), (a2, b1), (x1, y2), (x2, y1)] # 4
                ]

                for swapped_wires in swapped_pairs_configurations:

                    # Input regular reflector
                    enigma = create_enigma_machine(rotors, reflector_name, ring_settings, initial_positions, plugboard_pairs)

                    # Rewire reflector
                    rewired_reflector_mapping = list(enigma.reflector.mapping)

                    for new_wiring in swapped_wires:
                        
                        # Get the pair to wire
                        char1, char2 = new_wiring

                        # Get their mapping in the alphabet
                        char1_idx = ALPHABET.index(char1)
                        char2_idx = ALPHABET.index(char2)
                        
                        # Update wiring to reflector
                        rewired_reflector_mapping[char1_idx] = char2
                        rewired_reflector_mapping[char2_idx] = char1

                    # Add new reflector to enigma machine
                    enigma.reflector.mapping = "".join(rewired_reflector_mapping)
                    
                    # Encode message
                    possible_message = enigma.encode(code)

                    # Check if any of the cribs in message
                    for crib in cribs:
                        if crib in possible_message:
                            possible_messages.append(possible_message)

    return possible_messages


if __name__ == "__main__":

    # ------------- Test 1 -----------

    # Rotate on Notches

    # Notches at Q E V.  
    rotors = "I II III"
    reflector = "B"
    ring_settings = "01 01 01"
    initial_positions = "Q E V"
    enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, [])

    # Rotate outermost once -> should rotate next -> should rotate next
    ciphertext = enigma.encode("X")

    # Print final positions: all should be rotated. 'Q E V' -> 'R F W'
    final_positions = " ".join(list(
        map(lambda rotor: rotor.position, enigma.rotors)
    ))

    # TEST 1 PASSED :)
    assert(final_positions == "R F W")

    # Test if turnover messed 
    ciphertext += enigma.encode("XXYZ")

    # Emulator result on these settings for 'XXXYZ' produced 'YUIIP'
    assert(ciphertext == 'YUILP')

    # --------------- TEST 2 -------------------------------------

    # Apply ring settings

    rotors = "I II III"
    reflector = "B"
    ring_settings = "01 02 03" # on emulator: 'A B C'
    initial_positions = "A A Z"
    enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, [])

    # Enter 'AAABBBCCC' on emulator produces 'KGGCSAETS' -> TEST 2 PASSED :)
    assert(enigma.encode('AAABBBCCC') == 'KGGCSAETS')

    # --------------  TEST 3 ----------------------------------

    # Extreme ring settings and positions

    ring_settings = "26 26 26" # on emulator: 'Z Z Z'
    initial_positions = "Z Z Z"
    enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, [])

    # Enter 'AAABBBCCC' on emulator produces 'BDZCSYAJZ' TEST PASSED
    assert(enigma.encode('AAABBBCCC') == 'BDZCSYAJZ')
    
    # --------------  TEST 4 ----------------------------------

    # Does an enigma machine on the initial settings return back its decoded message?

    test_word = "TESTWORD"
    enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, [])
    encoded_message = enigma.encode(test_word)

    # Set enigma back to original settings
    enigma = create_enigma_machine(rotors, reflector, ring_settings, initial_positions, [])
    assert(enigma.encode(encoded_message) == test_word)
