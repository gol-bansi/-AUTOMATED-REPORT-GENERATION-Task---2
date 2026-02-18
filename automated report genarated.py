import requests
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# ---------------- CONFIG ----------------
API_KEY = "0c021de7c555436fd411e62f45e17713"
CITY = "Mumbai"
PDF_FILE = "Extended_Weather_Report.pdf"
CHART_FILE = "temperature_chart.png"
# ----------------------------------------

def fetch_weather(city):
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def create_temperature_chart(data):
    times = []
    temps = []

    for item in data["list"][:8]:  # next 24 hours (3-hour interval)
        times.append(item["dt_txt"][11:16])
        temps.append(item["main"]["temp"])

    plt.figure()
    plt.plot(times, temps, marker="o")
    plt.title("Temperature Trend (Next 24 Hours)")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close()

def generate_pdf(data):
    doc = SimpleDocTemplate(
        PDF_FILE,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("🌦️ Weather Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    # Meta info
    now = datetime.now().strftime("%d %B %Y, %H:%M")
    elements.append(Paragraph(f"<b>City:</b> {CITY}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Generated:</b> {now}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # Current weather table
    current = data["list"][0]
    table_data = [
        ["Metric", "Value"],
        ["Temperature (°C)", current["main"]["temp"]],
        ["Feels Like (°C)", current["main"]["feels_like"]],
        ["Humidity (%)", current["main"]["humidity"]],
        ["Pressure (hPa)", current["main"]["pressure"]],
        ["Weather", current["weather"][0]["description"].title()],
        ["Wind Speed (m/s)", current["wind"]["speed"]],
    ]

    table = Table(table_data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(Paragraph("Current Weather Summary", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Chart section
    elements.append(Paragraph("Temperature Trend", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(Image(CHART_FILE, width=400, height=250))
    elements.append(Spacer(1, 20))

    # Footer
    elements.append(Paragraph(
        "Data Source: OpenWeatherMap | Generated using Python",
        styles["Italic"]
    ))

    doc.build(elements)

if __name__ == "__main__":
    weather_data = fetch_weather(CITY)
    create_temperature_chart(weather_data)
    generate_pdf(weather_data)
    print("✅ Extended weather report generated:", PDF_FILE)
