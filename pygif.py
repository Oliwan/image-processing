from struct import *
class GIFError(Exception): pass

class GIF_FILE:       
    class image_block:
        def __init__(self,lp,tp,w,h,pf,lct,lzw,data):
            self.left_position = lp
            self.top_position = tp
            self.img_width = w
            self.img_height = h
            self.packed_field = pf
            self.local_color_table = lct
            self.lzw_minimum_code_size = lzw
            self.packed_image_data = data
            self.code_stream = []
            self.index_stream = []
            
        def code_unpack(self):
            # Little endian decoding with variable code size alà GIF

            # Initialization
            actual_code_size = self.lzw_minimum_code_size + 1 # we need to read lowest 4 bits of info and go on
            i = 0
            bits_already_read = 0
            bits_to_be_read = actual_code_size

            #Codelen is used to simulate the numbers of LZW of code table
            #Code table increase of +1 for each code found in stream (but first)
            #Clear code resets codelen too
            #TODO: we should include LZW decoding inside the unpacking process to avoid coupling with codelen
            codelen = 2**self.lzw_minimum_code_size + 1 # 0 - 7 i codici normali + CC + EOI
            primo = False

            while (i < len(self.packed_image_data)):
                #print "*** NEW BYTE ***"
                #print "codelen",codelen,"bar",bits_already_read,"b2br",bits_to_be_read,"code size",actual_code_size
                if bits_to_be_read < actual_code_size and bits_to_be_read > 0:
                    if bits_to_be_read > 8:
                        H_bits_remaining = (self.packed_image_data[i]) & 255
                        H_bits_remaining = H_bits_remaining << (actual_code_size - bits_to_be_read)
                        code = H_bits_remaining + code

                        bits_to_be_read -= 8
                        i += 1
                        continue
                    else:
                        H_bits_remaining = (self.packed_image_data[i]) & (255 >> (8 - min(bits_to_be_read,8)))
                        H_bits_remaining = H_bits_remaining << (actual_code_size - bits_to_be_read)
                        code = H_bits_remaining + code

                        if code == 2**self.lzw_minimum_code_size:
                            #print code,"Clear Code"
                            codelen = 2**self.lzw_minimum_code_size +1
                            actual_code_size = self.lzw_minimum_code_size + 1
                            self.code_stream.append(code)
                        elif code == 2**self.lzw_minimum_code_size + 1:
                            #print code,"End of Information Code"
                            actual_code_size = self.lzw_minimum_code_size + 1
                            #ignore next bits and align to next Lowest bit of new byte
                            i += 1
                            codelen = 2**self.lzw_minimum_code_size + 1
                            self.code_stream.append(code)
                            bits_already_read = 0
                            bits_to_be_read = actual_code_size
                            continue
                        else:
                            #print code
                            codelen += 1

                            if codelen >= 2**actual_code_size:
                                actual_code_size += 1
                                #print code,"codelen: ",codelen,"increaseds code size to",actual_code_size
                                if actual_code_size == 13:
                                    actual_code_size = 12 #and next code should be a CC
                            self.code_stream.append(code)

                        bits_already_read = bits_to_be_read
                        bits_to_be_read = actual_code_size
                else:
                    bits_already_read = 0

                #per il byte corrente
                while bits_already_read < 8:
                    #print "codelen",codelen,"bar",bits_already_read,"b2br",bits_to_be_read,"code size",actual_code_size
                    code = (self.packed_image_data[i] >> bits_already_read) & (255 >> (8 - min(bits_to_be_read,8)))

                    bits_already_read += actual_code_size
                    if bits_already_read > 8:
                        bits_to_be_read = bits_already_read - 8
                    else:
                        bits_to_be_read = min(bits_already_read % 8,actual_code_size)

                    if bits_to_be_read == actual_code_size or bits_to_be_read == 0:
                        if code == 2**self.lzw_minimum_code_size:
                            #print code,"Clear Code"
                            actual_code_size = self.lzw_minimum_code_size + 1
                            codelen = 2**self.lzw_minimum_code_size +1
                            self.code_stream.append(code)
                        elif code == 2**(self.lzw_minimum_code_size) + 1:
                            #print code,"End of Information Code"
                            actual_code_size = self.lzw_minimum_code_size + 1
                            #ignore next bits and align to next Lowest bit of new byte
                            #i += 1
                            codelen = 2**self.lzw_minimum_code_size + 1
                            self.code_stream.append(code)
                            bits_already_read = 0
                            bits_to_be_read = actual_code_size
                            break
                        else:
                            #print code
                            codelen += 1
                            if codelen >= 2**actual_code_size:
                                #print code,"codelen:",codelen,"increased code size to",actual_code_size
                                actual_code_size += 1
                                if actual_code_size == 13:
                                    actual_code_size = 12 #and next code should be a CC
                            self.code_stream.append(code)
                            bits_to_be_read = actual_code_size
                i += 1
                
        def code_pack(self,code_stream,lzw_minimum_code_size):
            # Little endian encoding with variable code size alà GIF
            # Initialization
            actual_code_size = lzw_minimum_code_size + 1 # we need to read lowest 4 bits of info and go on
            i = 0
            bits_already_written = 0
            bits_to_write = actual_code_size

            #Codelen is used to simulate the numbers of LZW of code table
            #Code table increase of +1 for each code found in stream (but first)
            #Clear code resets codelen too
            #TODO: we should include LZW decoding inside the unpacking process to avoid coupling with codelen
            codelen = 2**lzw_minimum_code_size + 1 # 0 - 7 i codici normali + CC + EOI
            
            byte_stream = []

            while i < len(code_stream):
                #print "*** New Byte ***"
                byte = 0
                bits_already_written = 0
                #print "interation:",i,"code:",code_stream[i]
                
                if bits_to_write > 0 and bits_to_write < actual_code_size:
                    if bits_to_write > 8:
                        byte = byte | ((code_stream[i] >> (actual_code_size - bits_to_write)) & 255)
                        bits_to_write -= 8
                        byte_stream.append(byte)
                        continue
                    
                    #print "need to write remaining part of",code_stream[i],"with code size:",actual_code_size,
                    #print "baw",bits_already_written,"b2w",bits_to_write
                    byte = byte | code_stream[i] >> ((actual_code_size - bits_to_write) & 255)
                    bits_already_written += bits_to_write
                    
                    if bits_already_written >= 8:
                        bits_to_write = bits_already_written - 8
                        byte_stream.append(byte)
                        #print "writing byte",byte,"b2w",bits_to_write,"baw",bits_already_written
                        if bits_to_write == actual_code_size or bits_to_write == 0:
                            bits_to_write = 0
                            if code_stream[i] == (2 ** lzw_minimum_code_size): #Clear Code
                                #print "Wrote Clear Code"
                                codelen = 2**lzw_minimum_code_size + 1
                                actual_code_size = lzw_minimum_code_size + 1
                            else:
                                codelen += 1
                                if codelen >= 2 ** actual_code_size:
                                    actual_code_size += 1
                                    #print "Increased code size to:",actual_code_size
                                    if actual_code_size == 13:
                                        actual_code_size = 12 #next code should be CC
                            #print "Finished with code",code_stream[i],"codelen",codelen
                            i += 1
                            if i >= len(code_stream):
                                break
                            
                    else:
                        bits_to_write = 0
                        if code_stream[i] == (2 ** lzw_minimum_code_size): #Clear Code
                            #print "Wrote Clear Code"
                            codelen = 2**lzw_minimum_code_size + 1
                            actual_code_size = lzw_minimum_code_size + 1
                        else:
                            codelen += 1
                            if codelen >= 2 ** actual_code_size:
                                actual_code_size += 1
                                #print "Increased code size to:",actual_code_size
                                if actual_code_size == 13:
                                    actual_code_size = 12 #next code should be CC
                        #print "Finished with code",code_stream[i],"codelen",codelen
                        i += 1
                        if i >= len(code_stream):
                            break
                    
                while bits_already_written < 8:
                    #print "need to write",code_stream[i],"with code size:",actual_code_size,
                    #print "baw",bits_already_written,"b2w",bits_to_write
                    byte = byte | ((code_stream[i] << bits_already_written) & 255)
                    
                    bits_already_written += actual_code_size
                    
                    if bits_already_written > 8:
                        bits_to_write = bits_already_written - 8
                    else:
                        bits_to_write = min(bits_already_written % 8, actual_code_size)
                    
                    #print "in questo caso b2w",bits_to_write,"baw",bits_already_written
                    if bits_to_write == actual_code_size or bits_to_write == 0:
                        if code_stream[i] == (2 ** lzw_minimum_code_size): #Clear Code
                            #print "Wrote Clear Code"
                            codelen = 2**lzw_minimum_code_size + 1
                            actual_code_size = lzw_minimum_code_size + 1
                        else:
                            codelen += 1
                            if codelen >= 2 ** actual_code_size:
                                actual_code_size += 1
                                #print "Increased code size to:",actual_code_size
                                if actual_code_size == 13:
                                    actual_code_size = 12 #next code should be CC
                        
                        #print "Finished with code",code_stream[i],"codelens",codelen
                        i += 1
                        if i >= len(code_stream):
                            byte_stream.append(byte)
                            #print "writing bytez",byte,"b2w",bits_to_write,"baw",bits_already_written
                            bits_to_write = bits_already_written - 8
                            bits_already_written = 0
                            if bits_to_write > 0 and bits_to_write < actual_code_size:
                                i -= 1
                            break
                    
                    if bits_already_written >= 8:
                        bits_to_write = bits_already_written - 8
                        byte_stream.append(byte)
                        #print "writing byted",byte,"b2w",bits_to_write,"baw",bits_already_written
                        bits_already_written = 0
                        break
                    else:
                        bits_to_write = 0
            
            print bits_already_written,bits_to_write,byte
            if bits_already_written > 0 and bits_already_written <8:
                print "Finally writing last piece of bits:",byte
                byte_stream.append(byte)
                
                
            return byte_stream
            
                
        def decompressLZW(self):
            def initialize_code_table():
                clear_code = 2**self.lzw_minimum_code_size
                code_table = dict((i,[i]) for i in xrange(2**self.lzw_minimum_code_size))
                code_table[clear_code] = "CC" #here a string was used for debugging issues
                code_table[clear_code+1] = "EOI" #here a string was used for debugging issues
                return code_table

            code = self.code_stream[0]
            code_table = initialize_code_table()

            code = self.code_stream[1]
            self.index_stream += code_table[code]

            skip = False

            for i in range(2,len(self.code_stream)):
                if skip:
                    skip = False
                    continue
                code = self.code_stream[i]
                if code in code_table:
                    if code_table[code] == "CC":
                        #print "CC found... re-initialize"
                        code_table = initialize_code_table()
                        j = i + 1
                        code = self.code_stream[j]
                        #print code,"should be inside table"
                        self.index_stream += code_table[code]
                        skip = True
                    elif code_table[code] == "EOI":
                        #print "End of Information"
                        break
                    else:
                        #print code_table[code]
                        self.index_stream += code_table[code]
                        k = code_table[code][0]
                        #print code
                        new_code = code_table[self.code_stream[i-1]] + [k]
                        code_table[len(code_table)] = new_code
                else:
                    #print "CODE not found"
                    k = code_table[self.code_stream[i-1]][0]
                    #print code
                    new_code = code_table[self.code_stream[i-1]] + [k]
                    self.index_stream += new_code
                    code_table[len(code_table)] = new_code
                    
        def compressLZW(self,lzw_minimum_code_size):
            def initialize_code_table():
                clear_code = 2**lzw_minimum_code_size
                eoi_code = 2**lzw_minimum_code_size + 1
                code_table = dict((chr(i),i) for i in xrange(2**lzw_minimum_code_size))
                code_table[str(clear_code)] = clear_code
                code_table[str(eoi_code)] = eoi_code
                return code_table,clear_code,eoi_code
            
            cs = []
            
            code_table,clear_code,eoi_code = initialize_code_table()
            
            #First output the Clear Code
            cs.append(clear_code)

            #Read first index
            index_buffer = chr(self.index_stream[0])

            for i in range(1,len(self.index_stream)):
                k = chr(self.index_stream[i])
                if index_buffer + k in code_table:
                    index_buffer += k
                    #print "Yes: new index_buffer =",index_buffer
                else:
                    code_table[index_buffer + k] = len(code_table)
                    cs += [code_table[index_buffer]]
                    index_buffer = k
                    if len(code_table) == 2**12+1: #max gif code size
                        #print "Clear Code needed",len(code_table)
                        cs += [clear_code]
                        code_table,clear_code,eoi_code = initialize_code_table()
                    #print "No: output",code_table[index_buffer],"and index_buffer =",index_buffer
            cs += [code_table[index_buffer]]
            cs += [eoi_code]
            return cs
            
    class extension_block:
        def __init__(self,block_data):
            self.block_data = block_data
            
            
    def __init__(self):
        self.blocks = []
        self.images = []
        
    def read_image(self,f):
        left_position = unpack("h",f.read(2)) # Left Position w.r.t. logical screen
        top_position = unpack("h",f.read(2)) # Top Position w.r.t. logical screen
        img_width = unpack("h",f.read(2)) # Width for block image
        img_height = unpack("h",f.read(2)) # Height for block image

        print ("Image data L:",left_position,"T:",top_position,
               "W:",img_width,"H:",img_height)

        #LOCAL COLOR TABLE (optional)
        packed_field = ord(f.read(1)) #Packed Field
        lct_present = packed_field & 128 == 128 # 1 000 0000 #First bit for Local Color Table present or not
        interlace = (packed_field & 64) >> 6 # 0100 0000 - Interlace
        sort_flag = (packed_field & 32) >> 5 # 0010 0000 - Sort Flag - 1 means ordering palette in decreasing frequency

        # 0001 1000 Reserved for future use

        size_of_lct = packed_field & 7 # 0000 0111 - Size of Global Color Table - 7 = 256 colors - 768 Bytes
        print ("Local Color Table present:",lct_present,"Interlace:",
           interlace,"Sort flag:",sort_flag,"Size of LCT:",size_of_lct)

        lct = []
        if lct_present: #read Local Color Table (usually not present)
            for i in range(0,2**(size_of_lct+1)):
                lct.append([ord(f.read(1)),ord(f.read(1)),ord(f.read(1))]) # R - G - B
            print lct

        lzw_minimum_code_size = ord(f.read(1))
        print "LZW minimum code:",lzw_minimum_code_size
        subblock_data = []
        subblock_size = ord(f.read(1))
        while subblock_size > 0:
            for i in range(subblock_size):
                subblock_data.append(ord(f.read(1)))
            #subblock_data = f.read(subblock_size)
            subblock_size = int(ord(f.read(1)))
        
        block = self.image_block(left_position,top_position,img_width,img_height,packed_field,lct,lzw_minimum_code_size,subblock_data)
        self.blocks.append(block)
        
        print "Image data read"

    def read_extension(self,f,intro_byte):
        block_data = []
        block_data.append(intro_byte)
        if intro_byte == 249: # 0xF9 Graphic Control Label
            print "GRAPHICS CONTROL EXTENSION (optional)"
            #Graphic control extension blocks are used frequently to specify transparency settings and control animations.
            byte_size = ord(f.read(1))
            packed_field = ord(f.read(1))
            delay_time = unpack("h",f.read(2))
            transparent_color_index = ord(f.read(1))
            block_terminator = ord(f.read(1))
            if block_terminator != 0: #block terminator
                raise GIFError('not a valid GIF file - Error in Graphic Control Extension')
                
            block_data.append(byte_size)
            block_data.append(packed_field)
            block_data.append(delay_time)
            block_data.append(transparent_color_index)
            block_data.append(block_terminator)
            
            block = self.extension_block(block_data)
            self.blocks.append(block)
            
            #print byte_size,packed_field,delay_time,transparent_color_index
        elif intro_byte == 255: # 0xFF Application Extension
            block_size = ord(f.read(1))
            application_identifier = f.read(block_size).decode("ASCII")
            subblock_size = ord(f.read(1))
            
            block_data.append(block_size)
            block_data.append(application_identifier)
            block_data.append(subblock_size)
            
            while subblock_size != 0:
                block_data.append(f.read(subblock_size))
                subblock_size = ord(f.read(1))
                block_data.append(subblock_size)
            print application_identifier
            
            block = self.extension_block(block_data)
            self.blocks.append(block)
        elif intro_byte == 254: # 0xFE Comment Extension
            #TODO: complete here
            print "Comment extension"
        else:
            raise GIFError('not a valid GIF extension')

    def read_block(self,f,introducer):
        self.blocks.append(introducer)
        if introducer == 33: # 0x21 Application Extension Introducer
            self.read_extension(f,ord(f.read(1)))
        elif introducer == 44: # 0x2C Image Separator
            self.read_image(f)

        introducer = ord(f.read(1))
        if introducer != 59: # 0x3B trailer and EOF
            self.read_block(f,introducer)
        else:
            print "Trailer found. End of File"
            
    
            
    def extract_images(self):
        for block in self.blocks:
            if isinstance(block,self.image_block):
                #unpack
                block.code_unpack()
                
                #decode
                block.decompressLZW()
                
                #return image -> self.images[]
        
    def read_gif_file(self,filename):
        with open(filename, 'rb') as f:
            #HEADER
            #read first 6 bytes from position 0            
            self.file_type = f.read(6)
            if self.file_type not in ('GIF87a', 'GIF89a'):
                raise GIFError('not a valid GIF file')

            #LOGICAL SCREEN DESCRIPTOR
            self.width = unpack("h",f.read(2))[0] #Canvas Width
            self.height = unpack("h",f.read(2))[0] #Canvas Height
            print "GIF file size:" , self.width , "x" , self.height

            self.packed_field = ord(f.read(1)) #Packed Field
            gct_present = self.packed_field & 128 == 128 # 1000 0000 #First bit for GCT present or not
            color_resolution = (self.packed_field & 56) >> 4 # 0111 0000 - Color resolution - 1 means 2 bits/pixel
            sort_flag = (self.packed_field & 8) >> 3 # 0000 1000 - Sort Flag - 1 means ordering palette in decreasing frequency
            size_of_gct = self.packed_field & 7 # 0000 0111 - Size of Global Color Table - 7 = 256 colors - 768 Bytes
            print ("Global Color Table present:",gct_present,"Color resolution:",
                   color_resolution,"Sort flag:",sort_flag,"Size of GCT:",size_of_gct)

            #Background Color Index
            #This is meaningful only if GCT is true. It represents wich color in the GCT should be used for pixels
            #whose value is not specified in the image data (for transparency)
            self.bg_color_index = ord(f.read(1))
            print "Background Color Index:",self.bg_color_index

            #Pixel Aspect Ratio - Not sure about this... Found always 0
            self.pixel_aspect_ratio = ord(f.read(1))
            print "Pixel aspect ratio:",self.bg_color_index

            #GLOBAL COLOR TABLE (optional)
            self.gct = []
            if gct_present:
                for i in range(0,2**(size_of_gct+1)):
                    self.gct.append([ord(f.read(1)),ord(f.read(1)),ord(f.read(1))]) # R - G - B
                #print gct

            self.read_block(f,ord(f.read(1)))    
            
        self.extract_images()
        
    def write_gif_file(self,filename):
        with open(filename, 'wb') as f:
            #HEADER
            #write first 6 bytes from position 0
            f.write(self.file_type)

            #LOGICAL SCREEN DESCRIPTOR
            f.write(pack('h',self.width))
            f.write(pack('h',self.height))
            
            f.write(chr(self.packed_field))

            f.write(chr(self.bg_color_index))
            f.write(chr(self.pixel_aspect_ratio))

            #GLOBAL COLOR TABLE (optional)
            for i in range(len(self.gct)):
                f.write(chr(self.gct[i][0]))
                f.write(chr(self.gct[i][1]))
                f.write(chr(self.gct[i][2]))

            #TODO: possibilmente utilizzare i meccanismi OO
            for block in self.blocks:
                if isinstance(block,int):
                    f.write(chr(block))
                elif isinstance(block,self.extension_block):
                    #print block.block_data
                    for element in block.block_data:
                        #print element
                        if isinstance(element,int):
                            f.write(chr(element))
                        elif isinstance(element,tuple):
                            f.write(pack('h',element[0]))
                        else:
                            f.write(element)
                else:
                    f.write(pack("h",block.left_position[0]))
                    f.write(pack("h",block.top_position[0]))
                    f.write(pack("h",block.img_width[0]))
                    f.write(pack("h",block.img_height[0]))
                    
                    f.write(chr(block.packed_field))
                    
                    for i in range(len(block.local_color_table)):
                        f.write(chr(block.local_color_table[i][0]))
                        f.write(chr(block.local_color_table[i][1]))
                        f.write(chr(block.local_color_table[i][2]))
                        
                    f.write(chr(block.lzw_minimum_code_size))
                    
                    i = 0
                    
                    #print block.packed_image_data
                    #writing subblock size
                    subblock_size = min(255,len(block.packed_image_data) -i)
                    #print "writing subblock size",subblock_size
                    f.write(chr(subblock_size))
                    while i < len(block.packed_image_data):
                        for j in range(subblock_size):
                            #print block.packed_image_data[i],
                            f.write(chr(block.packed_image_data[i]))
                            i += 1
                        #print len(block.packed_image_data),i
                        subblock_size = min(255,len(block.packed_image_data) - i)
                        #print "writing subblock size",subblock_size
                        f.write(chr(subblock_size))
                            
                    #nothing more to be read
                    #f.write(chr(0))
            
            #all blocks written
            #close file with trailer
            f.write(chr(59))