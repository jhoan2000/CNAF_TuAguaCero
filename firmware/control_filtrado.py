from machine import Pin
# --- Variables protegidas ---

bomba_pin = Pin(34, Pin.OUT)
val_pin = Pin(33, Pin.OUT)


def control(bomba_pin, val_pin, estado_bomba, estado_valvula):
    bomba_pin.value(estado_bomba)
    val_pin.value(estado_bomba)

def sistema_filtrado(umbrales_agua_filtrada, umbrales_agua_cruda,
             distancia_agua_cruda, distancia_agua_filtrada,
             sistema_purgado, control_manual):
    global bomba_pin, val_pin

    umbral_max_af, umbral_min_af = umbrales_agua_filtrada
    umbral_max_ac, umbral_min_ac = umbrales_agua_cruda
    bomba = None
    val_purga = None

    def purgar_agua():
        print("Purgando agua...")
        val_purga = True
        bomba = False
    def iniciar_filtrado():
        nonlocal bomba, val_purga
        print("Iniciando filtrado...")
        bomba = True
        val_purga = False
    def detener_sistema():
        nonlocal bomba, val_purga
        print("Deteniendo sistema...")
        bomba = False
        val_purga = False

    def filtado_automatico():
        print("Modo automático activado")
        if distancia_agua_cruda > umbral_min_ac:
            if distancia_agua_filtrada <= umbral_min_af:
                if not sistema_purgado:
                    purgar_agua()
                else:
                    iniciar_filtrado()
            elif distancia_agua_filtrada > umbral_min_af and distancia_agua_filtrada < umbral_max_af:
                iniciar_filtrado()
            elif distancia_agua_filtrada >= umbral_max_af:
                detener_sistema()
        else:
            detener_sistema()

    def arrancar_sistema():
        if control_manual == 2: # Purgar
            purgar_agua()
            iniciar_filtrado()
        elif control_manual == 1: # Detener
            detener_sistema()
        elif control_manual == 0: # Automático
            filtado_automatico()

    arrancar_sistema()

    control(bomba_pin, val_pin, estado_bomba=bomba, estado_valvula=val_purga)

    return bomba, val_purga
    

bomba, val_purga = sistema_filtrado(
    umbrales_agua_filtrada=(70, 20),
    umbrales_agua_cruda=(80, 30),
    distancia_agua_cruda=45,
    distancia_agua_filtrada=18,
    sistema_purgado=True,
    control_manual=0  # automático
)

print("Estado bomba:", bomba)
print("Estado válvula purga:", val_purga)
