import time

# --- Variables protegidas ---


def sistema(umbrales_agua_filtrada, umbrales_agua_cruda,
             distancia_agua_cruda, distancia_agua_filtrada,
             sistema_purgado, control_manual):
    
    umbral_max_af, umbral_min_af = umbrales_agua_filtrada
    umbral_max_ac, umbral_min_ac = umbrales_agua_cruda
    bomba = False
    val_purga = False

    def purgar_agua():
        val_purga = True

    def iniciar_filtrado():
        bomba = True

    def filtado_automatico():
        if distancia_agua_cruda > umbral_min_ac:
            if distancia_agua_filtrada <= umbral_min_af:
                if not sistema_purgado:
                    purgar_agua()
                else:
                    iniciar_filtrado()
            elif distancia_agua_filtrada > umbral_min_af and distancia_agua_filtrada < umbral_max_ac:
                iniciar_filtrado()
            elif distancia_agua_filtrada >= umbral_max_ac:
                bomba = False
        else:
            bomba = False
            val_purga = False

    def detener_sistema():
        bomba = False
        val_purga = False

    def arrancar_sistema():
        if control_manual == 2: # Purgar
            purgar_agua()
            iniciar_filtrado()
        elif control_manual == 1: # Detener
            detener_sistema()
        elif control_manual == 0: # Automático
            filtado_automatico()

    filtado_manual()

    return bomba, val_purga
    