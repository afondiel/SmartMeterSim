import gradio as gr
import pandas as pd
import json
import argparse
import time
import os

# Setup command-line arguments
parser = argparse.ArgumentParser(description="SmartMeterSim Gradio Dashboard")
parser.add_argument("--logFile", required=True, help="Path to the MQTT received data log file")
args = parser.parse_args()

LOG_FILE = args.logFile

def load_data():
    try:
        if not os.path.exists(LOG_FILE):
            return pd.DataFrame(columns=["timestamp", "energy_kW"])
        with open(LOG_FILE, "r") as file:
            data = json.load(file)
            df = pd.DataFrame(data)
            df['energy_kW'] = df['energy_kW'].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y')
            return df.head(10)  # Show first 10 readings
    except json.JSONDecodeError:
        print("Error decoding JSON from log file.")
        return pd.DataFrame(columns=["timestamp", "energy_kW"])
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=["timestamp", "energy_kW"])

def update_data(df):
    while True:
        time.sleep(1)
        new_data = load_data()  # Load only new or changed data
        df.update(value=new_data)
        yield

def generate_dashboard(plot_type, show_power, show_timestamp):
    df = load_data()
    if df.empty:
        return df, gr.update(visible=False), gr.update(visible=False)

    # Filter columns based on checkboxes
    columns_to_show = []
    if show_timestamp:
        columns_to_show.append("timestamp")
    if show_power:
        columns_to_show.append("energy_kW")
    
    df_filtered = df[columns_to_show]

    table_update = gr.update(value=df_filtered, visible=(plot_type == "Table"))
    line_plot_update = gr.update(
        value=df_filtered,
        x="timestamp" if show_timestamp else None,
        y="energy_kW" if show_power else None,
        title="Energy Consumption Over Time",
        tooltip=columns_to_show,
        visible=(plot_type == "Line Plot"),
        height="50vh"
    )
    bar_plot_update = gr.update(
        value=df_filtered,
        x="timestamp" if show_timestamp else "energy_kW",
        y="energy_kW" if show_power else None,
        title="Energy Consumption Distribution",
        tooltip=columns_to_show,
        visible=(plot_type == "Histogram"),
        height="50vh"
    )

    return table_update, line_plot_update, bar_plot_update

custom_css = """
@media (min-width: 768px) {
    .plot-container {
        height: 500px !important;
    }
}
@media (max-width: 767px) {
    .plot-container {
        height: 50vh !important;
    }
}
"""

with gr.Blocks(css=custom_css) as app:
    gr.Markdown("<h1 style='text-align: center;'>⚡ SmartMeterSim Dashboard ⚡</h1>")
    gr.Markdown("<h3 style='text-align: center;'>📈 Optimize your energy footprint instantly with real-time usage data.</h3>")
    
    with gr.Row():
        with gr.Column(scale=2):  # Sidebar (20% width)
            gr.Markdown("## 💡 Measurements")
            measure_power = gr.Checkbox(label="Power", value=True)
            measure_timestamp = gr.Checkbox(label="Timestamp", value=True)
            
            gr.Markdown("## 📊 Graphs")
            plot_type = gr.Dropdown(["Table", "Line Plot", "Histogram"], value="Table", label="Select Visualization")
            
            refresh_btn = gr.Button("🔄 Refresh Data")
        
        with gr.Column(scale=8):  # Main content (80% width)
            df_display = gr.Dataframe(value=load_data(), label="Energy Data Table", interactive=False)
            app.load(lambda: update_data(df_display))
            line_plot = gr.LinePlot(visible=False, height="50vh", elem_classes="plot-container")
            bar_plot = gr.BarPlot(visible=False, height="50vh", elem_classes="plot-container")

    refresh_btn.click(
        fn=generate_dashboard,
        inputs=[plot_type, measure_power, measure_timestamp],
        outputs=[df_display, line_plot, bar_plot]
    )
    
    plot_type.change(
        fn=generate_dashboard,
        inputs=[plot_type, measure_power, measure_timestamp],
        outputs=[df_display, line_plot, bar_plot]
    )

app.queue()
app.launch()
