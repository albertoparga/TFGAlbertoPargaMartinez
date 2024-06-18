import ee
import datetime
import time
import os

# Nombre del archivo donde se guardará el nombre del proyecto
archivo_proyecto = 'nombre_proyecto.txt'

def auth():
    try:
        # Autenticar el usuario con la cuenta de Google Earth Engine
        ee.Authenticate()
        return 0
    except Exception as e:
        return e

def init(proyecto): 
    try: 
        # Inicializar el proyecto de Google Earth Engine
        ee.Initialize(project=proyecto)
        return 0
    except Exception as e:
        return e
    
def getCount():
    try:
        print('Calculando recuento de píxeles')

        # Definir la geometría dentro de la cual se hará el recuento de píxeles, en este caso corresponde a la ciudad de Madrid y alrededoress
        geometry = ee.Geometry.Polygon(
            [[[-3.994472420624886, 40.58277967781604],
            [-3.994472420624886, 40.178983009608395],
            [-3.318813240937386, 40.178983009608395],
            [-3.318813240937386, 40.58277967781604]]])

        # Rango de fechas
        yearStart = 2016
        yearEnd = datetime.datetime.now().year
        monthEnd = datetime.datetime.now().month

        startDate = []
        endDate = []

        # Gestión de los primeros meses
        startDate.append('2015-07-01')
        endDate.append('2015-09-30')
        startDate.append('2015-10-01')
        endDate.append('2015-12-31')

        # Recorrer los años entre yearStart y yearEnd
        for year in range(yearStart, yearEnd):
            # Definir las fechas de inicio y fin para cada trimestre
            trimestres = {
                1: {
                    'inicio': (f'{year}-01-01'),
                    'fin': (f'{year}-03-31')
                },
                2: {
                    'inicio': (f'{year}-04-01'),
                    'fin': (f'{year}-06-30')
                },
                3: {
                    'inicio': (f'{year}-07-01'),
                    'fin': (f'{year}-09-30')
                },
                4: {
                    'inicio': (f'{year}-10-01'),
                    'fin': (f'{year}-12-31')
                }
            }

            # Recorrer los trimestres y generar las fechas de inicio y fin
            for trimestre in trimestres:
                startDate.append(trimestres[trimestre]['inicio'])
                endDate.append(trimestres[trimestre]['fin'])

        # Gestión del año actual
        if monthEnd <= 6:
            startDate.append((f'{yearEnd}-01-01'))
            endDate.append((f'{yearEnd}-03-31'))
        elif monthEnd <= 9:
            startDate.append((f'{yearEnd}-01-01'))
            endDate.append((f'{yearEnd}-03-31'))
            startDate.append((f'{yearEnd}-04-01'))
            endDate.append((f'{yearEnd}-06-30'))
        elif monthEnd <= 12:
            startDate.append((f'{yearEnd}-01-01'))
            endDate.append((f'{yearEnd}-03-31'))
            startDate.append((f'{yearEnd}-04-01'))
            endDate.append((f'{yearEnd}-06-30'))
            startDate.append((f'{yearEnd}-07-01'))
            endDate.append((f'{yearEnd}-09-30'))

        # Obtener imágenes de Dynamic World V1, filtrando por las coordenadas correspondientes
        dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterBounds(geometry)
            
        dwVisParams = {
            'min': 0,
            'max': 8,
            'palette': [
                '#419BDF', '#397D49', 
                '#88B053', '#7A87C6', 
                '#E49635', '#DFC35A',
                '#C4281B', '#A59B8F', 
                '#B39FE1'
            ]
        }

        dws = []
        classification = []
        dwComposite = []
        pixelCountStats = []
        pixelCounts = []
        combinedFc = ee.FeatureCollection([])

        for i in range(len(startDate)):
            try: 
                # Filtrar por el trimestre correspondiente
                dws.append(dw.filterDate(startDate[i], endDate[i]))
                
                # Crear un modo composite
                classification.append(dws[i].select('label'))
                dwComposite.append(classification[i].reduce(ee.Reducer.mode()))
                dwComposite[i] = dwComposite[i].rename([f'classification{i}'])
                
                pixelCountStats.append(dwComposite[i].reduceRegion(
                    reducer=ee.Reducer.frequencyHistogram().unweighted(),
                    geometry=geometry,
                    scale=10,
                    maxPixels=1e10,
                ))
                
                pixelCounts.append(ee.Dictionary(pixelCountStats[i].get(f'classification{i}')))
            
                print(f"Conteo de píxeles {i} completado. De {startDate[i]} a {endDate[i]}")

                # Añadir las fechas para cada conteo de píxeles
                featureProperties = pixelCounts[i].combine({
                    'startDate': startDate[i],
                    'endDate': endDate[i]
                })
                
                combinedFc = combinedFc.merge(ee.FeatureCollection(ee.Feature(None, featureProperties)))
            except Exception as e:
                print(f'Error in iteration {i}:', e)

        # Exportar a Google Drive
        task = ee.batch.Export.table.toDrive(
            collection=combinedFc,
            description='pixel_counts_export',
            folder='earthengine',
            fileFormat='CSV'
        )

        print(f"Exportando CSV a Google Drive. Encontrará el archivo en la carpeta /earthengine.")
        task.start()

        # Función para verificar el estado de la tarea
        def check_task_status(task_id):
            status = ee.data.getTaskStatus(task_id)[0]
            return status['state']

        # Esperar a que la tarea se complete
        task_id = task.id
        while True:
            status = check_task_status(task_id)
            print(f"Estado de la exportación: {status}")
            if status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(10)  # Esperar 10 segundos antes de volver a verificar

        if status == 'COMPLETED':
            return 0
        elif status == 'FAILED':
            return "Failed export"

    except Exception as e:
        return e

# Función para leer el nombre del proyecto desde el archivo
def leer_nombre_proyecto(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r') as file:
            nombre_proyecto = file.read().strip()
            return nombre_proyecto
    return None

# Función para guardar el nombre del proyecto en el archivo
def guardar_nombre_proyecto(archivo, nombre_proyecto):
    with open(archivo, 'w') as file:
        file.write(nombre_proyecto)

# Función para borrar el contenido de un archivo
def borrar_contenido_archivo(archivo):
    with open(archivo, 'w') as file:
        pass  # Abrir en modo 'w' automáticamente borra el contenido

# Función para obtener el nombre del proyecto
def proyect():
    # Intentar leer el nombre del proyecto desde el archivo
    mi_proyecto = leer_nombre_proyecto(archivo_proyecto)

    # Si el archivo no existe o está vacío, pedir al usuario el nombre del proyecto
    if not mi_proyecto:
        mi_proyecto = input("Por favor, introduzca el nombre de su proyecto de Google Earth Engine: ")
        guardar_nombre_proyecto(archivo_proyecto, mi_proyecto)
        
    return mi_proyecto


if __name__ == "__main__":
    autenticacion = auth()
    if autenticacion == 0:
        mi_proyecto = proyect()
        initialize = init(mi_proyecto)
        if initialize == 0:
            result = getCount()
            if result == 0:
                print("Ejecución completada correctamente.")
            else:
                print("Error count. Ejecución fallida durante el recuento de píxeles: ", result)
        else:
            print("Error init. Fallo al acceder al proyecto: ", initialize)
            borrar_contenido_archivo(archivo_proyecto)
    else:
        print("Error auth. Fallo en la autenticación:", autenticacion)