def h(letra):
    j=2
    def dosveces():
        print(j) 
        return letra * 2
           
    return dosveces()
print(h("x"))  # Esto imprimirá "xx"