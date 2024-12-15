import math

# FUNCTION 1
def load_file(file_name: str) -> (bytes, str):
    d = open(file_name, "rb")
    data = d.read()
    info = str(file_name)
    if len(data) != 0:
        return (data, info)
    else:
        return (bytes())
        return ('file not found')


# FUNCTION 2
def get_file_header(data):
    if data[0:2] == b'II':
        byte_order = 'little'
    else:
        byte_order = 'big'
    ifd_offset = int.from_bytes(data[4:8], byte_order)  # have byte_order in the brackets so that it knows which
    return (byte_order, ifd_offset)


# FUNCTION 3
def extract_ifd_entries(data, byte_order, ifd_offset) -> (list, int):
    element_size = 12
    ifd_entries_N = int.from_bytes(data[ifd_offset: ifd_offset + 2],
                                   byte_order)  # remember to include the byte_order, as this tells the code the order of data in the file
    ifd_entries = [] * ifd_entries_N  # making an empty list with as many possible spots as directory entries
    for i in range(ifd_entries_N):
        start = ifd_offset + 2 + (i * element_size)  # to get past the 2 bytes of number of directory entries
        end = start + element_size
        ifd_entry = data[start: end]
        ifd_entries.append(ifd_entry)
    return (ifd_entries, ifd_entries_N)


# FUNCTION 4
def extract_ifd_entry(ifd_entry, byte_order):
    field_tag = int.from_bytes(ifd_entry[0: 2], byte_order)
    dictionary_location = int.from_bytes(ifd_entry[2: 4],
                                         byte_order)  # the field_type is a location, and this location is associated then with a name and a size
    tiff_field_types = {
        1: "BYTE",  # the key is the location given, the value is the name associated with it
        2: "ASCII",
        3: "SHORT",
        4: "LONG",
        5: "RATIONAL",
    }
    tiff_field_types_size = {
        1: 1,  # the key is the location given, the value is the size of the type (how many bytes)
        2: 1,
        3: 2,
        4: 4,
        5: 8,
    }
    field_types_size = tiff_field_types_size.get(dictionary_location, "Unknown Field Type Size")  # getting information from the dictionary
    field_types_name = tiff_field_types.get(dictionary_location, "Unknown Field Types")
    number_of_values = int.from_bytes(ifd_entry[4: 8], byte_order)
    value_offset = ifd_entry[8: 12]
    field_entry = [field_tag, field_types_name, field_types_size, number_of_values, value_offset]
    return (field_entry)


# FUNCTION 5
def extract_field_values(data, field_entry, byte_order):
    field_tag = field_entry[0]
    field_types_name = field_entry[1]  # extracting the information from the previous function
    value_offset_int = int.from_bytes(field_entry[4], byte_order)
    value = []  # making an empty list to hold the values
    field_value = {
        field_tag: value  # a dictionary with a single key:value entry
    }

    if field_types_name == 'BYTE':  # testing the type of each entry, to convert the bytes into the correct thing
        value.append(bytes(data[field_entry[4]]))  # this covers for when the value offset is greater than can be stored directly in the
    elif field_types_name == 'ASCII':
        value.append(data[value_offset_int: value_offset_int + field_entry[3] - 1].decode('utf-8'))
    elif field_types_name == 'SHORT':
        if field_entry[3] == 1:  # the number of values
            value.append(value_offset_int)
        else:
            for i in range(field_entry[3]):
                value_SHORT = bytes(data[value_offset_int: value_offset_int + 2])  # makes sure to go through all the bytes that a variable 'short' has, which is 2
                value.append(int.from_bytes(value_SHORT, byte_order))
    elif field_types_name == 'LONG':
        if field_entry[3] == 1:
            value.append(field_entry[3])
        else:
            for i in range(field_entry[3]):
                value_LONG = bytes(data[value_offset_int: value_offset_int + 4])  # makes sure to go through all the bytes that a variable 'long' has, which is 4
                value.append(int.from_bytes(value_LONG, byte_order))
    elif field_types_name == 'RATIONAL':  # since a float is a value that has decimals/is fractional, will have a numerator and denominator value
        numerator = data[value_offset_int: value_offset_int + 4]  # getting the bytes of the numerator, and then denominator
        denominator = data[value_offset_int + 4: value_offset_int + 8]  # the front 4 bytes make up the numerator value; the back 4 bytes make up the denominator
        value.append(int.from_bytes(numerator, byte_order) / int.from_bytes(denominator, byte_order))
    return (field_value)


# FUNCTION 6
def extract_image(data, field_values, byte_order):
    image_length = (field_values[257])[0]  # extracting the first element of the dictionary it was directed to by the image width tag
    image_width = (field_values[256])[0]  # extracting the first element of the dictionary it was directed to by the the image length tag
    img = []
    
    for row in range(image_length): #1st dimension of image
        image_row = []
        for col in range(image_width): #2nd dimension of image; and the columns per row are each respectively red, green then blue
            red = data[(row * image_width + col) * 3 + 8] #extracting the colour from data: multiplied by 3 since red is found every 3 values, but the rbg data starts at a different offset every time??
            green = data[(row * image_width + col) * 3 + 1 + 8]
            blue = data[(row * image_width + col) * 3 + 2 + 8]
            image_row.append([red, green, blue]) #adding each column to each row
        img.append(image_row) #adding each row to the whole array, which is a list but without square brackets (kind of)
    return (img)
