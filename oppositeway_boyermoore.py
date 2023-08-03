import sys


"""
A function used to read the two text files. One of the input file contains the text and the other contains the pattern.

"""
def readInput(txtFileName, patFileName):
    # Open and read the txt file
    txtFile = open(txtFileName, 'r')
    txt = txtFile.read()

    # Close the file
    txtFile.close()

    # Open and read the pattern file
    patFile = open(patFileName, 'r')
    pat = patFile.read()

    # Close the file
    patFile.close()

    # Return the pattern and text
    return txt, pat


"""
A function used to write the output of oppositeway_boyermoore() to the output file output_oppositeway_boyermoore.txt. Each position where pat matches txt will be in a seperate line.   

"""
def writeOutput(occurrences):
    # Open output file with correct name
    outputFile = open("output_oppositeway_boyermoore.txt", "w")

    # if occurrences is empty such as there is no pat or txt or both
    if occurrences == []:
        outputFile.write("")

    else:
        # Iterate through the occurrence list and write results to an output file
        outputFile.write(str(occurrences[0] + 1))
        for i in range(1, len(occurrences)):
            outputFile.write('\n')
            outputFile.write(str(occurrences[i] + 1))

    # Close the file
    outputFile.close()


"""
A binary search function used to find the index of the leftmost occurence of the bad character to the right of the point of mismatch

"""
def binary_search(bc_list, j):
    left = 0
    right = len(bc_list) - 1

    while left <= right:
        mid = (left + right) // 2 + 1 # Will get the floor index. 4 + 5 // 2 = 4. Then + 1 to get the ceiling value 

        #* Goal: bc_list[mid] needs to be > j but the leftmost occurence 

        # Check if item at index mid is > j and item at mid - 1 is <= j
        # if true, it means that mid is the smallest number > j        
        if bc_list[mid] > j and bc_list[mid - 1] <= j:
            return bc_list[mid]

        elif bc_list[mid] > j:     
            right = mid - 1 # right = mid - 1 because if it enters this condition then we know that bc_list[mid - 1] is still > j

        elif bc_list[mid] < j:
            left = mid


"""
z algo for prefixes

"""
def zalgo(pat):
    z = [None] * len(pat) 
    z[0] = len(pat) # first position is the length of pat

    # variables 
    l, r = 0, 0
    matches = 0
    i = 1 

    for i in range(1, len(pat)):
        
        # Case 1: i is outside the box
        if i > r:
            pointer = i
            j = 0
            matches = 0

            # compare outside box, matches += 1 each time character match
            while pointer < len(pat) and pat[j] == pat[pointer]:
                j += 1
                pointer += 1
                matches += 1
        
            # Form the z-box
            if matches > 0:
                z[i] = matches
                l = i
                r = i + matches - 1
            
            else: 
                z[i] = 0

        # Case 2a, 2b, 2c: i is inside the box
        else: 
            k = i - l # index of prefix which corresponds to the index of substring that matches
            remaining = r - i + 1

            # case 2a: z[k] < remaining
            if z[k] < remaining:
                z[i] = z[k]

            # case 2b: z[k] > remaining
            elif z[k] > remaining:
                z[i] = remaining
            
            # case 2c: z[k] == remaining
            elif z[k] == remaining:
                matches = remaining 

                # compare outside box, matches += 1 each time character match
                pointer1 = r - i + 1  
                pointer2 = r + 1
                
                while pointer2 < len(pat) and pat[pointer1] == pat[pointer2]:
                    matches += 1
                    pointer1 += 1
                    pointer2 += 1

                # Form the z-box
                z[i] = matches
                l = i 
                r = i + matches - 1

    return z

"""
A Boyer-Moore algorithm running in the opposite way. Finds all the exact occurrences of pat in txt. 

"""
def oppositeway_boyermoore(txt, pat):
    
    # if txt or pat or both are empty, return empty list
    if txt == "" or pat == "":
        return []

    else:

        # preprocessing
        z_array = zalgo(pat)

        # bc_array is used as an array linked list to store the character index of pat in order to find the 
        # leftmost character to the right of the mismatch for shifting to the left. 
        bc_array = [None] * (127-32+1) 
        gs_array = [0] * (len(pat)+1) # good suffix array 
        mp_array = [0] * (len(pat)+1) # matched prefix array 
        result = []  # An array to store the start index of the occurences
        mismatch = 0
        
        # fill up bc_array array linked list -> build: O(M) , space: O(M) , Access = O(log m) = Amortized O(1)
        for i in range(len(pat)):
            # initialize alpha in pat to ascii 
            alpha = ord(pat[i]) - 32 # so that the 1st printable ascii starts from 0  

            # check if bc_array[alpha] == None 
            if bc_array[alpha] == None:
                bc_array[alpha] = [] # Initialize empty list 
                bc_array[alpha].append(i) # Append index of pat to the empty list at index of alpha in bc_array

            # contains an existing list 
            else:
                bc_array[alpha].append(i) # Append index of pat to the existing list at index of alpha in bc_array

        # fill up gs_array 
        for i in range(len(pat)-1, 0, -1): # Loop from m to 1 where m is the last char of pat. index 0 is not included because the value will be same as length
            j = z_array[i]
            gs_array[j] = i 

        # fill up mp_array 
        # Loop from back to front of pattern starting from len(pat) - 2 
        for i in range(len(pat)-1, -1, -1):

            # if z_array[i] + i == len(pat) - 1, it means that the value is equal to the length of pat
            # Therefore, there exist a suffix at position z_array[i]
            if z_array[i] + i == len(pat) - 1: 
                mp_array[i] = z_array[i]

            # if z_array[i] + i != len(pat) - 1, it means that the value does not equal to the length of pat
            # Therfore, it is not a suffix. 
            # Since it is not a suffix, we re-use the value at mp_array[i+1] at mp_array[i]
            elif z_array[i] + i != len(pat) - 1 and i < len(pat): 
                mp_array[i] = mp_array[i + 1]



        # shift movement: Right to Left
        # Comparison: Left to Right 
        pat_start = len(txt) - len(pat) # used to indicate the left endpoint of pat after shifting to the left 
        pat_end = len(pat) - 1
        shift = 0

        # This loop executes only when pat_start - shift is >= 0 because the pattern will be out of bounds if it does not meet this requirement
        while pat_start - shift >= 0:

            # needs to be reset to 0 in a new iteration 
            pat_start -= shift 
            pat_pointer = 0 # used in pat for comparing pat with txt
            txt_pointer = pat_start
            matched_length = 0 # length of characters that are matched 
            match = True # check if match or not

            # shifts 
            bc_shift = 0
            gs_shift = 0
            mp_shift = 0
            shift = 0

            # Comparison movement: Left to Right
            while pat_pointer <= len(pat) - 1 and match == True:
                #! TODO: Galil's Optimisation

                # Check for a between pat[pat_pointer] and txt[txt_pointer], if match then increment the 2 pointers and matched length
                if pat[pat_pointer] == txt[txt_pointer]:
                    pat_pointer += 1
                    txt_pointer += 1
                    matched_length += 1

                    # Full match
                    if matched_length == len(pat):
                        mp_shift = len(pat) - mp_array[1] # Since it is a full match, shift pat by len(pat) - mp_array[1]
                        result.append(pat_start) # Append pat_start to the result list. pat_start is the start point of the pat

                # mismatch occurs
                elif pat[pat_pointer] != txt[txt_pointer]:
                    match = False 
                    mismatch_txt = txt_pointer # index of mismatch in txt as we want to find bad character which is in txt

                    # Bad Character Rule
                    alpha = ord(txt[mismatch_txt]) - 32 # Get the ascii value of the bad character
                    bc_list = bc_array[alpha] # Find the bad character list in the bc_array which returns a list of occurrences 

                    if bc_list == None:
                        bc_shift = len(pat) # if there is no bad_char to the right of the mismatch, shift by len(pat)

                    else:
                        # Do a binary search on bc_list to find index of alpha where smallest alpha > pat_pointer 
                        # Ex: alpha = [1,2], pat_pointer = 0 ; binary search result = 1 

                        # Checks if len(bc_list) is greater than 0 in order to do binary search
                        if len(bc_list) > 1:
                            pat_index = binary_search(bc_list, pat_pointer) # Execute binary search on the bc_list and get the pat_index use for shifting

                        else: 
                            pat_index = bc_list[0] # if there is only 1 element then pat_index is bc_list[0] 

                        bc_shift = pat_index - pat_pointer # shift the pat to the left by pat_index - pat_pointer positions


                    # Good Suffix Rule

                    # This condition is used to check if pat_pointer is 0 or not. if its 0 then it wont enter this condition as it means there is no suffix yet
                    if pat_pointer != 0:
                        if gs_array[pat_pointer] > 0: # If this is true, it means there exist a leftmost suffix to the right of the mismatch where the rightmost char is not the same as the mismatched char in pat 
                            gs_shift = gs_array[pat_pointer] # shift the pat to the left by the gs_array[pat_pointer]
                        
                        # There is no simillar suffix to the right of the mismatch, therefore matched prefix is used 
                        elif gs_array[pat_pointer] == 0:
                            # Matched Prefix  
                            gs_shift = len(pat) - mp_array[pat_pointer - 1] - 1  # shift the pat to the left by len(pattern) - mp_array[pat_pointer - 1] - 1 positions.

            shift = max(bc_shift, gs_shift, mp_shift) # The max of bc_shift, gs_shift and mp_shift is stored in shift 

        return result 


if __name__ == "__main__":
    # First retrieve the file names from the console
    txtFileName = sys.argv[1]
    patFileName = sys.argv[2]

    # Read in the text and pattern from these files
    txt, pat = readInput(txtFileName, patFileName)

    # Process the text and pattern
    occurrences = oppositeway_boyermoore(txt, pat)  # occurrences is a list of tuples

    # Write your output to a correctly named file
    writeOutput(occurrences)
