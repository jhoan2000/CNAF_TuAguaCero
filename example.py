# Numero entero
uno = 1
print(uno)
print(type(uno))

# Numero flotante
decimal = 2.5
print(decimal)
print(type(decimal))

# Cadena de texto
texto = "Hola, mundo"
print(texto)
print(type(texto))

# Cadena de texto
texto = 'Hola, mundo'
print(texto)
print(type(texto))

# Boleano
verdadero = True
print(verdadero)
print(type(verdadero))

falso = False
print(falso)  
print(type(falso))

# Lista
print("----- Lista -----")
lista = [1, "50", False, 4.5, [5]]
print(lista)
print(type(lista))
# iteración de lista o recorrer lista
for i in lista:
    print(i, type(i))
    
# Acceder a un elemento de la lista
print("Ejemplo de acceso a un elemento de la lista")
cincuenta = lista[1]
print(cincuenta)  # "50"
print(type(cincuenta))  # str
# cambiar un elemento de la lista
lista[1] = "Fernando"
print(lista)  # [1, 50, False, 4.5, [5]]

# lista vacía
print("----- Lista vacía -----")
nombres_familia = []
print(nombres_familia)
nombres_familia.append("Indira")
print(nombres_familia)
nombres_familia.append("Fernando")
print(nombres_familia)

# tupla
print("----- Tupla -----")
tupla = (1, "50", False, 4.5, [5])

print(tupla)
print(type(tupla))  

# diccionario

print("----- Diccionario -----")