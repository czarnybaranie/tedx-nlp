from pathlib import Path

from shiny import ui
import pandas as pd
import json

dtype = {
    "translated_title": "str",
}

app_dir = Path(__file__).parent
df = pd.read_csv(app_dir / "FINAL_TEDX_DATASET_2024.csv", dtype=dtype, low_memory=False)
with open(app_dir / "markers.geojson") as f:
    geojson_data = json.load(f)


def show_category_notification():
    ui.notification_show(
        f"Categories were created using fine-tuned Bart LLM model achieving 0.81 AUC score on multi-label (32 labels) classification task. Therefore they sometimes may not be accurate.",
        type="message",
        duration=10,
    )


def show_map_notification():
    ui.notification_show(
        f"The map is rendering, please wait...",
        type="message",
        duration=10,
    )


def show_map_description():
    m = ui.modal(
        ui.HTML(
            """
        <b>Important note:</b><br><br>
        The map was prepared automatically using geopy library based on the event organizer's name. Therefore, the location may not be accurate. The location latitude and longitude were only found in 3741 out of 10162 unique event organizers (36.8%).<br><br>
        <b>Example:</b><br><br>
        TEDxSGH was geocoded to the location of the Singapore General Hospital (SGH) instead of the actual location of the event in Warsaw, Poland.
        """
        ),
        easy_close=True,
    )
    ui.modal_show(m)


def show_sentiment_notification():
    m = ui.modal(
        ui.HTML(
            """
        Sentiment analysis was performed using a fine-tuned BERT model achieving 0.99 accuracy. The fined-tuned model was trained on a dataset labeled in the following way:<br><br>
        <b>1. Positive sentiment:</b> Includes titles that convey optimism, inspiration, motivation, or hope. This category combines elements of positivity and inspiration, offering insight into titles that aim to motivate or uplift.<br><br>
        <b>2. Negative sentiment:</b> Encompasses titles that communicate pessimism, criticism, anxiety, or difficult emotions. This category can serve as an indicator of titles that address challenging topics or evoke negative emotions.<br><br>
        <b>3. Neutral sentiment:</b> Covers titles that are informational, educational, or factual in nature, with a neutral emotional tone. This category is useful for identifying titles that focus primarily on conveying knowledge without a strong emotional charge.
        """
        ),
        easy_close=True,
    )
    ui.modal_show(m)
