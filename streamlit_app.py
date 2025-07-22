import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/). Que pasa muñones!!!"
)
# Instalar dependencias y librerias necesarias
!pip install qrcode pandas matplotlib openpyxl pillow

import pandas as pd
import qrcode
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
from PIL import Image

# PASO 1: Importamos el fichero Excel con direcciones y tipo de zona
from google.colab import files
uploaded = files.upload()  # Función para subir el Excel

# Obtener nombre del fichero
excel_filename = list(uploaded.keys())[0]

# Leer el archivo Excel
df = pd.read_excel(excel_filename)

# Expandir la lista de etiquetas según la cantidad
expanded_labels = []
expanded_zones = []
for _, row in df.iterrows():
    for _ in range(int(row['CANTIDAD'])):
        expanded_labels.append(row.iloc[0])  # Dirección
        expanded_zones.append(row.iloc[1])  # Zona

df_expanded = pd.DataFrame({'LABELS': expanded_labels, 'ZONES': expanded_zones})

# 📌 PASO 2: Configurar la página (A4 con etiquetas y espaciado)
A4_width, A4_height = 210, 297  # Tamaño de A4 en mm
cols, rows = 3, 7  # Número de etiquetas por fila y columna
spacing = 0  # Espaciado entre etiquetas
text_height = 10  # Espacio reservado para el texto de la etiqueta

# Ajustar el tamaño de cada etiqueta considerando el espacio entre ellas
x_spacing = (A4_width - (cols - 1) * spacing) / cols
y_spacing = (A4_height - (rows - 1) * spacing) / rows

# 📌 PASO 3: Definir colores de fondo para los códigos QR según la zona
zone_colors = {
    "PAS": "white",
    "ISL": "white",
    "POD": "#A7C7E7",  # Light Cornflower Blue 3
    "CDE": "#7EA7D3",  # Light Cornflower Blue 2
    "CTR": "#7EA7D3",  # Light Cornflower Blue 2
    "XSL": "#90EE90",  # Light Green 3
    "CAJ": "#FFFF99",  # Light Yellow 3
    "EXP": "#FF9999",  # Light Red 3
    "IMP": "#A7C7E7",  # Light Cornflower Blue 3
    "ALT": "#FFA07A",  # Light Orange 3
}

# 📌 PASO 4: Función para generar el PDF con etiquetas y QR
def generate_a4_labels(labels, zones, cols, rows, page_size, filename):
    pdf = PdfPages(filename)
    labels_per_page = cols * rows

    label_width = page_size[0] / cols   # Use page_size[0] which is A4_width
    label_height = page_size[1] / rows  # Use page_size[1] which is A4_height
    text_height = 10  # mm

    for page_start in range(0, len(labels), labels_per_page):

#        fig, ax = plt.subplots(figsize=(page_size[0] / 25.4, page_size[1] / 25.4))  # Convert mm to inches
#  **Mod:** Creamos la fig sin margenes en la hoja
        fig = plt.figure(figsize=(page_size[0] / 25.4, page_size[1] / 25.4), dpi=300) # Convert mm to inches, high DPI
#  **Mod:** Añadimos ejes que cubren la figura entera para asegruarnos de quitar los margenes.
        ax = fig.add_axes([0, 0, 1, 1]) # [left, bottom, width, height] in figure coordinates (0 to 1)

        ax.set_xlim(0, page_size[0])
        ax.set_ylim(0, page_size[1])
        ax.axis('off')

#  **Mod:** Invertimos el eje Y para que el origen de coordenadas vertical sea la esquina de arriba a la izquierda para que sea más facil gestionar
        ax.invert_yaxis()

        for i in range(labels_per_page):
            if page_start + i >= len(labels):
                break

            label = labels[page_start + i]
            zone = zones[page_start + i]
            row = i // cols
            col = i % cols

            x = col * label_width
            y = row * label_height

            # Contorno de etiqueta ** He quitado el contorno para que sea mas ligible al etiqueta **
#            ax.add_patch(plt.Rectangle((x, y), label_width, label_height, linewidth=1, edgecolor='black', facecolor='none'))

            # Linea/Recuadro para el texto ** He cambiado el recuadro por una linea debajo del texto **
# **Mod: Descomentar si queremos recuadro**            ax.add_patch(plt.Rectangle((x, y + label_height - text_height), label_width, text_height, linewidth=1, edgecolor='black', facecolor='none'))
            line_y_position = y + text_height # Caluclamos la posición vertical de la línea debajo del texto
            ax.plot([x, x + label_width], [line_y_position, line_y_position], color='black', linewidth=1)
            # 📌 Generar código QR con el color de fondo según la zona
            qr_bg_color = zone_colors.get(str(zone).strip().upper(), "white")  # Obtener color o usar blanco por defecto

            qr = qrcode.QRCode(box_size=10, border=4)
            qr.add_data(label)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color=qr_bg_color).convert("RGB")

            # Definir tamaño del QR y del fondo de color
            qr_percentage = 0.7
            # Calculamos el espacio disponible para el QR
            available_height_for_qr = label_height - text_height
            qr_size = min(label_width * qr_percentage, available_height_for_qr * qr_percentage)


            # Ajustamos la posición horizontal debajo del texto
            qr_x = x + (label_width - qr_size) / 2
            # Ajustamos la posición vertical del QR debajo del texto. Posición relativa respecto a la esquina superior IZQ de la hoja.
            qr_y = y + text_height + (available_height_for_qr - qr_size) / 2


            # Dibujar el rectángulo de fondo de color ANTES del QR
#  **Mod: Comentamos, parte del codigo innecesario**
#            ax.add_patch(plt.Rectangle(
#                (qr_x - (qr_bg_size - qr_size) / 2, qr_y - (qr_bg_size - qr_size) / 2),  # Ajuste para centrarlo
#                qr_bg_size, qr_bg_size, facecolor=qr_bg_color, edgecolor='none', zorder=0
#            ))

            # Convertir QR en imagen de Matplotlib
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            qr_img_array = plt.imread(qr_buffer)

            # Insertar QR en la etiqueta sobre el fondo de color
            ax.imshow(qr_img_array, extent=[qr_x, qr_x + qr_size, qr_y, qr_y + qr_size], zorder=1)

            # Añadimos el texto relativo a la dirección
# Si queremos aumentar el tamaño de texto cambiamos el parámetro "fontsize"
# Si queremos mover el texto hacia abajo modificamos el parámetro offset_texto. Si queremos bajarlo aumentamos el valor, si queremos subirlo lo reducimos.
#            ax.text(x + x_spacing / 2, y + y_spacing - text_height / 2, label, fontsize=11, ha='center', va='center', fontweight='bold')
            offset_texto = 3.5
            ax.text(x + label_width / 2, (y + text_height / 2) + offset_texto, label, fontsize=10, ha='center', va='center', fontweight='bold')

        # Guardar la página en el PDF
        pdf.savefig(fig, bbox_inches='tight', pad_inches=0)
        plt.close(fig)

    pdf.close()

#  PASO 5: Ejecutar la generación del PDF
# Podemos modificar el nombre del fichero
a4_spaced_filename = "etiquetas_A4_sin_espacio.pdf"
generate_a4_labels(
    df_expanded['LABELS'].tolist(),  # Lista de direcciones
    df_expanded['ZONES'].tolist(),  # Lista de tipos de zona
    cols, rows, (A4_width, A4_height),
    a4_spaced_filename
)

# 📌 Descargar el PDF generado
files.download(a4_spaced_filename)
