import re, itertools, random

# Define global constants: the character set we will be enocding
CHARACTER_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 *,.()[]#@+-=_\/'^%$£!?<>:;`“”^|"

class RotorBox:
    def __init__(self) -> None:
        # Create temporary dictionary for rotors
        self.items = {}

        # Add rotors to box
        existing_mappings = []
        for rotor_name in ["I", "II", "III", "IV", "V", "Beta", "Gamma"]:

            # Pick notch randomly and shuffle alphabet to create mapping
            mapping = random.sample(CHARACTER_SET, len(CHARACTER_SET))

            # Ensure the mapping hasn't been created before
            while mapping in existing_mappings:

                # Pick notch randomly and shuffle alphabet to create mapping
                mapping = random.sample(CHARACTER_SET, len(CHARACTER_SET))

            existing_mappings.append(mapping)

            # Beta and gamma do not have notches
            if rotor_name in ["Beta", "Gamma"]:
                notch = None
            else:
                notch = random.sample(CHARACTER_SET, 1)

            # Add rotor to box
            self.items[rotor_name] = ("".join(mapping), notch)

        # Add reflectors to box
        existing_positions = []
        for reflector_name in ["A", "B", "C"]:

            # Create a shuffled list of all the positions between 0 - extended character set
            positions = list(range(len(CHARACTER_SET)))
            random.shuffle(positions)

            while positions in existing_positions:
                random.shuffle(positions)

            existing_positions.append(positions)

            # Create the reflector mapping
            reflector_mapping = list(CHARACTER_SET)
            while len(positions) != 0:

                rand_idx_1 = positions.pop()
                rand_idx_2 = positions.pop()

                # Obtain two random positions
                char1, char2 = CHARACTER_SET[rand_idx_1], CHARACTER_SET[rand_idx_2]

                # Switch positions
                reflector_mapping[rand_idx_1], reflector_mapping[rand_idx_2] = char2, char1

            reflector_mapping = "".join(reflector_mapping)

            # Add reflector to box
            self.items[reflector_name] = (reflector_mapping, None)

    def rotor_from_name(self, rotor_name: str) -> object:
        """
        Method which returns a Rotor object the given name of the Rotor e.g. I or Gamma.
        """
        # Get row data for a rotor name
        rotor_mapping, rotor_notch_position = self.items[rotor_name]

        # Return the resulting rotor object
        return Rotor(rotor_name, rotor_mapping, rotor_notch_position)


# define rotor box as a global variable
rotor_box = RotorBox()


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
        alphabet_index = CHARACTER_SET.index(character)

        # 2. Find the no. places the rotor has been shifted
        offset = CHARACTER_SET.index(self.position) - self.ring_setting       

        # 3. Get the index of the current pin
        pin_index = (alphabet_index + offset) % len(CHARACTER_SET)

        # 4. Find the contact of the current rotor 
        current_contact = self.mapping[pin_index]

        # 5. Translate the contact back to the correct pin for the next rotor
        next_contact_index = (CHARACTER_SET.index(current_contact) - offset) % len(CHARACTER_SET)

        # 6. Return the contact for the next rotor
        return CHARACTER_SET[next_contact_index]

    def encode_left_to_right(self, character):
        """
        Mapping |-> Alphabet
        """
        # 1. Find the position of the current character in the alphabet
        alphabet_index = CHARACTER_SET.index(character)

        #2. Find the no. places the rotor has been shifted
        offset = CHARACTER_SET.index(self.position) - self.ring_setting

        # 3. Get the index of the current contact
        contact_index = (alphabet_index + offset) % len(CHARACTER_SET)

        # 4. Find the pin for the current rotor's contact
        current_pin = CHARACTER_SET[contact_index]

        # 5. Translate the pin back to the correct pin for the next rotor
        next_pin_index = (self.mapping.index(current_pin) - offset) % len(CHARACTER_SET)

        # 6. Return the pin for the next rotor
        return CHARACTER_SET[next_pin_index]

    def rotate(self) -> bool:
        """
        Updates the position of a rotor after rotation. If the last position  a notch, function returns True.
        """
        # Create a variable to remember whether the last position was a notch
        notch_was_rotated = self.position == self.notch_position

        # move the rotor one position up | if this is the last position-> loop back to 0
        alphabet_index = (CHARACTER_SET.index(self.position) + 1) % len(CHARACTER_SET)
        
        # Update the new position after rotation
        self.position = CHARACTER_SET[alphabet_index]

        # Indicate whether the notch has been rotated
        return notch_was_rotated


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
        new_rotor = rotor_box.rotor_from_name(names_of_rotors[rotor_idx])

        # Assign the rotor's ring_setting and initial_position
        new_rotor.ring_setting = ring_settings[rotor_idx]
        new_rotor.position = initial_positions[rotor_idx]

        # Add new rotor object
        rotors.append(new_rotor)

    # Create the reflector
    reflector = rotor_box.rotor_from_name(reflector_name)

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
