import gradio as gr
import pandas as pd
import json
import argparse
import time

# Setup command-line arguments
parser = argparse.ArgumentParser(description="SmartMeterSim Gradio Dashboard")
parser.add_argument("--logFile", required=True, help="Path to the MQTT received data log file")
args = parser.parse_args()

LOG_FILE = args.logFile

def load_data():
    try:
        with open(LOG_FILE, "r") as file:
            data = json.load(file)
            df = pd.DataFrame(data)
            df['energy_kW'] = df['energy_kW'].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y')
            return df.tail(10)  # Show last 10 readings
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=["timestamp", "energy_kW"])

def generate_dashboard(plot_type):
    df = load_data()
    if df.empty:
        return df, None, None

    if plot_type == "Line Plot":
        plot = gr.LinePlot(
            value=df,
            x="timestamp",
            y="energy_kW",
            title="Energy Consumption Over Time",
            tooltip=["timestamp", "energy_kW"],
            width=700,
            height=400,
        )
    elif plot_type == "Histogram":
        plot = gr.BarPlot(
            value=df,
            x="energy_kW",
            y="energy_kW",
            title="Energy Consumption Distribution",
            tooltip=["energy_kW"],
            width=700,
            height=400,
        )
    else:
        plot = None

    return df, plot, plot_type

with gr.Blocks() as app:
    gr.Markdown("# ⚡ Smart Meter Real-Time Dashboard")
    gr.Markdown("📡 Live energy consumption data from AWS IoT")

    with gr.Row():
        plot_type = gr.Dropdown(["Table", "Line Plot", "Histogram"], value="Table", label="Select Visualization")
        refresh_btn = gr.Button("🔄 Refresh Data")

    df_display = gr.Dataframe(value=load_data, label="Energy Data Table", interactive=False)
    plot_display = gr.Plot(label="Visualization")

    refresh_btn.click(
        fn=generate_dashboard,
        inputs=[plot_type],
        outputs=[df_display, plot_display, plot_type]
    )

    plot_type.change(
        fn=generate_dashboard,
        inputs=[plot_type],
        outputs=[df_display, plot_display, plot_type]
    )

app.launch()
