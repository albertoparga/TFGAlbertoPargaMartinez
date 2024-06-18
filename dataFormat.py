import pandas as pd

def format(csv_path):
    # Intentar leer el archivo CSV con pandas
    try:
        df = pd.read_csv(csv_path)
        print("Archivo CSV cargado correctamente.")

        # Eliminar columnas innecesarias
        df = df.drop(columns=["system:index", ".geo"])

        # Formateor las fechas para eliminar datos de hora
        df["startDate"] = df["startDate"].str.split("T").str[0]
        df["endDate"] = df["endDate"].str.split("T").str[0]

        # Renombrar columnas
        new_column_names = ['water', 'trees', 'grass', 'flooded_vegetation', 'crops', 'shrub_and_scrub', 'built', 'bare', 'snow_and_ice']
        df.columns = [new_column_names[i] if i < len(new_column_names) else df.columns[i] for i in range(len(df.columns))]


        # Convertir a enteros (excepto fechas)
        for col in df.columns:
            if col not in ["startDate", "endDate"]:
                try:
                    df[col] = df[col].astype(int)
                except ValueError:
                    print(f"Warning: Columna '{col}' no se pudo convertir en enteros.")
                    exit()

        # Guardar DataFrame formateado
        output_path = csv_path.replace(".csv", "_formatted.csv")
        df.to_csv(output_path, index=False)

        print("Datos formateados")
        return 0
    except FileNotFoundError:
        return 1
    except pd.errors.EmptyDataError:
        return 2
    except pd.errors.ParserError:
        return 3
    except Exception as e:
        return e

if __name__ == "__main__":
    csv_path = "pixel_counts_export.csv" #input("Por favor, introduce la ruta del archivo CSV: ")
    
    # Llamar a la función de formato y obtener el código de salida
    result = format(csv_path)
    
    # Revisar el código de salida para determinar si hubo un error o si se completó correctamente
    if result == 0:
        print("Ejecución completada correctamente.")
    elif result == 1:
        print(f"Error e1: El archivo '{csv_path}' no fue encontrado.")
    elif result == 2:
        print("Error e2: El archivo está vacío.")
    elif result == 3:
        print("Error e3 : Hubo un problema al parsear el archivo.")
    else:
        print(f"Error e4: {result}")
