def maksimal_kemahiran(N, M, Ai, Bi):
    lawan = list(zip(Ai, Bi))

    #Urutin
    lawan.sort(key=lambda x: (x[0], -x[1]))
    
    for a, b in lawan:
        if M >= a:  
            M += b  
        else:
            #Jika kalah
            break  
    
    return M

# Contoh Input 1
N = 4
M = 2
Ai = [8, 9, 3, 2]
Bi = [5, 4, 1, 3]
print(maksimal_kemahiran(N, M, Ai, Bi))  # Output: 6

# Contoh Input 2
N = 5
M = 3
Ai = [8, 4, 5, 6, 7]
Bi = [9, 8, 7, 5, 6]
print(maksimal_kemahiran(N, M, Ai, Bi))  # Output: 3

# Contoh Input 3
N = 5
M = 9
Ai = [2, 3, 6, 7, 8]
Bi = [3, 4, 2, 2, 3]
print(maksimal_kemahiran(N, M, Ai, Bi))  # Output: 23
