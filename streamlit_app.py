import streamlit as st
import pandas as pd
import qrcode
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Generador de etiquetas QR", layout="centered")

st.title("📦 Generador de etiquetas QR en PDF")
st.markdown("Sube un archivo Excel con columnas **Dirección, Cantidad Etiquetas, Zona** para generar etiquetas.")

uploaded_file = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx" , "ods"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        # Expandir según cantidad
        expanded_labels = []
        expanded_zones = []
        for _, row in df.iterrows():
            for _ in range(int(row['CANTIDAD ETIQUETAS'])):
                expanded_labels.append(row.iloc[0])  # Dirección
                expanded_zones.append(row.iloc[2])  # Zona

        df_expanded = pd.DataFrame({'LABELS': expanded_labels, 'ZONES': expanded_zones})

        A4_width, A4_height = 210, 297
        cols, rows = 3, 7
        text_height = 10

        zone_colors = {
            "PAS": "white", "ISL": "white", "POD": "#A7C7E7",
            "CDE": "#7EA7D7", "CTR": "#7EA7D7", "XSL": "#90EE90", "CAR": "#7EA7D7",
            "CAJ": "#90EE90", "EXP": "#FFA07A", "IMP": "#90EE90", "ALT": "#FFA07A",
            "10": "#FFFF14",  "20": "#FFA500",  "30": "#A7C7E7",  "40": "#90EE90",  "50": "#FF00FF",  "PC": "white",
        }

        def generate_a4_labels(labels, zones, cols, rows, page_size):
            pdf_buffer = io.BytesIO()
            pdf = PdfPages(pdf_buffer)

            label_width = page_size[0] / cols
            label_height = page_size[1] / rows
            text_height = 10

            labels_per_page = cols * rows

            for page_start in range(0, len(labels), labels_per_page):
                fig = plt.figure(figsize=(page_size[0] / 25.4, page_size[1] / 25.4), dpi=300)
                ax = fig.add_axes([0, 0, 1, 1])
                ax.set_xlim(0, page_size[0])
                ax.set_ylim(0, page_size[1])
                ax.axis('off')
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

                    line_y_position = y + text_height
                    ax.plot([x, x + label_width], [line_y_position, line_y_position], color='black', linewidth=1)

                    qr_bg_color = zone_colors.get(str(zone).strip().upper(), "white")

                    qr = qrcode.QRCode(box_size=10, border=4)
                    qr.add_data(label)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color=qr_bg_color).convert("RGB")

                    qr_percentage = 0.7
                    available_height_for_qr = label_height - text_height
                    qr_size = min(label_width * qr_percentage, available_height_for_qr * qr_percentage)

                    qr_x = x + (label_width - qr_size) / 2
                    qr_y = y + text_height + (available_height_for_qr - qr_size) / 2

                    qr_buffer = io.BytesIO()
                    qr_img.save(qr_buffer, format="PNG")
                    qr_buffer.seek(0)
                    qr_img_array = plt.imread(qr_buffer)

                    ax.imshow(qr_img_array, extent=[qr_x, qr_x + qr_size, qr_y, qr_y + qr_size], zorder=1)

                    offset_texto = 3.5
                    ax.text(x + label_width / 2, (y + text_height / 2) + offset_texto, label, fontsize=10, ha='center', va='center', fontweight='bold')

                pdf.savefig(fig, bbox_inches='tight', pad_inches=0)
                plt.close(fig)

            pdf.close()
            pdf_buffer.seek(0)
            return pdf_buffer

        st.success("✅ Archivo leído correctamente.")
        if st.button("📄 Generar etiquetas PDF"):
            pdf_bytes = generate_a4_labels(
                df_expanded['LABELS'].tolist(),
                df_expanded['ZONES'].tolist(),
                cols, rows, (A4_width, A4_height)
            )
            st.download_button("⬇️ Descargar PDF", data=pdf_bytes, file_name="etiquetas.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
